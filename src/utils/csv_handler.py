import csv
import io
import re
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash
from database.models import (
    Person, Curator, Role, Group, Student, Parent,
    HobbyType, PostInGroupType, SocialStatus, StudentInGroup
)
from utils.formatters import format_group_name

PHONE_REGEX = re.compile(r"^[0-9\s\-\(\)\+]+$")

def parse_csv(file_stream) -> list[dict]:
    file_stream.seek(0)
    raw = file_stream.read()
    text = None
    for encoding in ('utf-8-sig', 'utf-8', 'cp1251', 'latin-1'):
        try:
            text = raw.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if text is None:
        raise ValueError("Не удалось прочитать файл. Сохраните CSV в UTF-8 или Windows-1251.")

    reader = csv.DictReader(io.StringIO(text))
    return [
        {k.strip(): v.strip() if v else "" for k, v in row.items()}
        for row in reader if any(row.values())
    ]

def detect_table_type(headers: list[str]) -> str | None:
    h = {x.lower() for x in headers}
    if {"surname", "name", "login", "password", "role_name"}.issubset(h): return "curators"
    if {"surname", "name"}.issubset(h) and "login" not in h and ("group_id" in h or "group_name" in h): return "students"
    if {"role_name"}.issubset(h): return "roles"
    if {"surname", "name"}.issubset(h) and "login" not in h: return "parents"
    if {"hobby_type_name"}.issubset(h): return "hobbies"
    if {"post_in_group_type_name"}.issubset(h): return "posts"
    if {"status_name"}.issubset(h): return "statuses"
    return None

def _resolve_group(db: Session, identifier: str) -> Group | None:
    """Находит группу по ID или по отформатированному имени (ИСП-121п)."""
    identifier = identifier.strip()
    if identifier.isdigit():
        return db.query(Group).filter_by(group_id=int(identifier)).first()
    
    target_name = identifier.lower()
    for g in db.query(Group).all():
        if format_group_name(g).lower() == target_name:
            return g
    return None

def import_data(db: Session, table_type: str, data: list[dict]) -> dict:
    errors = []
    success_count = 0

    for row_idx, row in enumerate(data, start=2):
        row_errors = []
        _validate_row(row, table_type, row_idx, db, row_errors)

        if row_errors:
            errors.extend(row_errors)
            continue

        try:
            _insert_row(db, table_type, row)
            success_count += 1
        except Exception as e:
            errors.append({"row": row_idx, "field": "БД", "value": "", "message": f"Ошибка сохранения: {e}"})

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        errors.append({"row": "-", "field": "Транзакция", "value": "", "message": f"Откат из-за: {e}"})

    return {"success_count": success_count, "errors": errors}

def _validate_row(row: dict, table_type: str, row_idx: int, db: Session, errors: list):
    def add_err(field, msg):
        errors.append({"row": row_idx, "field": field, "value": row.get(field, ""), "message": msg})

    if table_type == "curators":
        for f in ["surname", "name", "login", "password", "role_name"]:
            if not row.get(f): add_err(f, "Обязательное поле")
        if row.get("phone") and not PHONE_REGEX.match(row["phone"]): add_err("phone", "Неверный формат")
        if db.query(Curator).filter_by(login=row.get("login", "").strip()).first():
            add_err("login", "Логин уже занят")
        if row.get("role_name") and not _get_role_id(db, row["role_name"]):
            add_err("role_name", "Роль не найдена")

    elif table_type == "students":
        for f in ["surname", "name"]:
            if not row.get(f): add_err(f, "Обязательное поле")
        
        group_val = row.get("group_id") or row.get("group_name")
        if not group_val:
            add_err("group_name", "Обязательное поле (укажите ID или имя группы)")
        elif not _resolve_group(db, group_val):
            add_err("group_name", f"Группа '{group_val}' не найдена в системе")

    elif table_type == "roles":
        if not row.get("role_name"): add_err("role_name", "Обязательное поле")
        elif db.query(Role).filter_by(role_name=row["role_name"].strip()).first(): add_err("role_name", "Уже существует")

    elif table_type == "parents":
        for f in ["surname", "name"]:
            if not row.get(f): add_err(f, "Обязательное поле")

    elif table_type in ["hobbies", "posts", "statuses"]:
        field_map = {"hobbies": "hobby_type_name", "posts": "post_in_group_type_name", "statuses": "status_name"}
        f_name = field_map[table_type]
        if not row.get(f_name): add_err(f_name, "Обязательное поле")

def _get_role_id(db, val):
    val = str(val).strip()
    if val.isdigit():
        return db.query(Role).filter_by(role_id=int(val)).first()
    return db.query(Role).filter_by(role_name=val).first()

def _insert_row(db, table_type, row):
    if table_type in ["curators", "students"]:
        p = Person(surname=row["surname"], name=row["name"], patronymic=row.get("patronymic"), phone=row.get("phone"))
        db.add(p); db.flush()
        if table_type == "curators":
            role = _get_role_id(db, row["role_name"])
            db.add(Curator(person_id=p.person_id, login=row["login"].strip(), 
                           password_hash=generate_password_hash(row["password"]), role_id=role.role_id))
        else:
            db.add(Student(person_id=p.person_id, is_expelled=False))
            db.flush()
            group_val = row.get("group_id") or row.get("group_name")
            group = _resolve_group(db, group_val)
            if group:
                db.add(StudentInGroup(student_id=p.person_id, group_id=group.group_id, creation_date=date.today()))
                
    elif table_type == "parents":
        db.add(Parent(surname=row["surname"], name=row["name"], patronymic=row.get("patronymic"), phone=row.get("phone")))
    elif table_type == "roles":
        db.add(Role(role_name=row["role_name"], role_description=row.get("description")))
    elif table_type == "hobbies":
        db.add(HobbyType(hobby_type_name=row["hobby_type_name"]))
    elif table_type == "posts":
        db.add(PostInGroupType(post_in_group_type_name=row["post_in_group_type_name"]))
    elif table_type == "statuses":
        db.add(SocialStatus(status_name=row["status_name"]))