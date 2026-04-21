import csv
import io
from werkzeug.security import generate_password_hash
from database.models import (
    Person, Curator, Role, Student, StudentInGroup, Group, 
    Parent, SocialStatus, HobbyType, PostInGroupType, 
    Specialization, Qualification, Course
)

def detect_table_type(headers):
    """Определяет тип таблицы по заголовкам CSV"""
    headers_lower = [h.lower().strip() for h in headers]
    
    if 'login' in headers_lower and 'password' in headers_lower:
        return 'curators'
    elif 'role_name' in headers_lower:
        return 'roles'
    elif 'hobby_type_name' in headers_lower:
        return 'hobbies'
    elif 'post_in_group_type_name' in headers_lower:
        return 'posts'
    elif 'status_name' in headers_lower:
        return 'statuses'
    elif 'specialization_name' in headers_lower and 'qualification_name' in headers_lower:
        return 'groups'
    elif 'surname' in headers_lower and 'phone' in headers_lower and 'login' not in headers_lower:
        return 'parents'
    elif 'surname' in headers_lower and ('group_id' in headers_lower or 'group_name' in headers_lower):
        return 'students'
    else:
        return None

def parse_csv(file_stream):
    """
    Читает поток файла CSV и возвращает список словарей.
    Поддерживает utf-8-sig (Excel) и обычный utf-8.
    """
    
    file_stream.seek(0)
    
    
    try:
        stream = io.TextIOWrapper(file_stream, encoding='utf-8-sig', newline='')
        reader = csv.DictReader(stream)
        data = list(reader)
        stream.detach()  
        return data
    except UnicodeDecodeError:
        
        file_stream.seek(0)
        stream = io.TextIOWrapper(file_stream, encoding='utf-8', newline='')
        reader = csv.DictReader(stream)
        data = list(reader)
        stream.detach()
        return data

def import_data(db, table_type, data):
    """Маршрутизатор импорта данных по типу таблицы"""
    success_count = 0
    errors = []
    redirect_url = "/admin/import"

    try:
        if table_type == 'curators':
            redirect_url = "/admin/curators"
            for idx, row in enumerate(data, start=2):  
                try:
                    
                    surname = row.get('surname', '').strip()
                    name = row.get('name', '').strip()
                    patronymic = row.get('patronymic', '').strip() or None
                    phone = row.get('phone', '').strip() or None
                    
                    if not surname or not name:
                        errors.append(f"Строка {idx}: пустые ФИО")
                        continue

                    
                    person = db.query(Person).filter(
                        Person.surname == surname,
                        Person.name == name,
                        (Person.phone == phone) | (phone is None)
                    ).first()
                    
                    if not person:
                        person = Person(
                            surname=surname,
                            name=name,
                            patronymic=patronymic,
                            phone=phone
                        )
                        db.add(person)
                        db.flush()  

                    
                    role = None
                    role_input = str(row.get('role_name', '')).strip()
                    
                    
                    if role_input and not role_input.isdigit():
                        role = db.query(Role).filter_by(role_name=role_input).first()
                    
                    
                    if not role and role_input.isdigit():
                        role = db.query(Role).get(int(role_input))
                    
                    
                    if not role:
                        role = db.query(Role).first()
                        if not role:
                            errors.append(f"Строка {idx}: нет ролей в системе")
                            continue

                    
                    login = row.get('login', '').strip()
                    password = row.get('password', '').strip()
                    
                    if not login or not password:
                        errors.append(f"Строка {idx}: пустой логин или пароль")
                        continue

                    existing = db.query(Curator).filter_by(person_id=person.person_id).first()
                    if not existing:
                        db.add(Curator(
                            person_id=person.person_id,
                            login=login,
                            password_hash=generate_password_hash(password),
                            role_id=role.role_id
                        ))
                    success_count += 1
                    
                except KeyError as e:
                    errors.append(f"Строка {idx}: отсутствует поле {e}")
                except Exception as e:
                    errors.append(f"Строка {idx}: {str(e)}")
                    db.rollback()

        elif table_type == 'roles':
            redirect_url = "/admin/roles"
            for idx, row in enumerate(data, start=2):
                name = row.get('role_name', '').strip()
                desc = row.get('description', '').strip() or None
                if name and not db.query(Role).filter_by(role_name=name).first():
                    db.add(Role(role_name=name, role_description=desc))
                    success_count += 1

        elif table_type == 'parents':
            redirect_url = "/admin/parents"
            for idx, row in enumerate(data, start=2):
                surname = row.get('surname', '').strip()
                name = row.get('name', '').strip()
                if surname and name:
                    existing = db.query(Parent).filter_by(
                        surname=surname, name=name, phone=row.get('phone', '').strip() or None
                    ).first()
                    if not existing:
                        db.add(Parent(
                            surname=surname,
                            name=name,
                            patronymic=row.get('patronymic', '').strip() or None,
                            phone=row.get('phone', '').strip() or None
                        ))
                        success_count += 1

        elif table_type == 'students':
            redirect_url = "/admin/students"
            for idx, row in enumerate(data, start=2):
                try:
                    surname = row.get('surname', '').strip()
                    name = row.get('name', '').strip()
                    if not surname or not name:
                        continue

                    person = db.query(Person).filter_by(surname=surname, name=name).first()
                    if not person:
                        person = Person(
                            surname=surname,
                            name=name,
                            patronymic=row.get('patronymic', '').strip() or None,
                            phone=row.get('phone', '').strip() or None
                        )
                        db.add(person)
                        db.flush()

                    if not db.query(Student).filter_by(person_id=person.person_id).first():
                        db.add(Student(person_id=person.person_id))

                    group_id = row.get('group_id', '').strip()
                    if group_id and group_id.isdigit():
                        if not db.query(StudentInGroup).filter_by(student_id=person.person_id).first():
                            db.add(StudentInGroup(
                                student_id=person.person_id,
                                group_id=int(group_id)
                            ))
                    success_count += 1
                except Exception as e:
                    errors.append(f"Студент {idx}: {str(e)}")

        elif table_type in ('hobbies', 'posts', 'statuses'):
            model_map = {
                'hobbies': (HobbyType, 'hobby_type_name', '/admin/hobbies'),
                'posts': (PostInGroupType, 'post_in_group_type_name', '/admin/posts'),
                'statuses': (SocialStatus, 'status_name', '/admin/social-statuses')
            }
            Model, name_field, url = model_map[table_type]
            redirect_url = url
            for idx, row in enumerate(data, start=2):
                name = row.get(name_field, '').strip()
                if name and not db.query(Model).filter_by(**{name_field: name}).first():
                    db.add(Model(**{name_field: name}))
                    success_count += 1

        db.commit()

    except Exception as e:
        db.rollback()
        errors.append(f"Критическая ошибка: {str(e)}")

    return success_count, errors, redirect_url