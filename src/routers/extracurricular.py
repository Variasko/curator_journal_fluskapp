from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import (
    StudentHobby,
    HobbyType,
    Student,
    Person,
    Group,
    StudentInGroup,
    Curator,
)

from utils.formatters import format_group_name

extracurricular_bp = Blueprint(
    "extracurricular", __name__, url_prefix="/extracurricular"
)


@extracurricular_bp.route("/", methods=["GET", "POST"])
def index():

    if "person_id" not in session:

        return redirect(url_for("login"))

    curator_id = session["person_id"]

    db: Session = SessionLocal()

    try:

        curator_groups = db.query(Group).filter_by(curator_id=curator_id).all()

        groups_data = [
            {"group_id": g.group_id, "display_name": format_group_name(g)}
            for g in curator_groups
        ]

        selected_group_id = request.args.get("group_id") or request.form.get("group_id")

        if not selected_group_id and groups_data:

            selected_group_id = groups_data[0]["group_id"]

        if request.method == "POST":

            action = request.form.get("action")

            student_id = request.form.get("student_id")

            hobby_ids = request.form.getlist("hobby_ids")

            if action == "delete" and student_id:

                db.query(StudentHobby).filter_by(student_id=int(student_id)).delete(
                    synchronize_session=False
                )

                db.commit()

                flash("Хобби удалены", "success")

                return redirect(
                    url_for("extracurricular.index", group_id=selected_group_id)
                )

            if action == "save" and student_id:

                db.query(StudentHobby).filter_by(student_id=int(student_id)).delete(
                    synchronize_session=False
                )

                for hid in hobby_ids:

                    if hid.isdigit():

                        db.add(
                            StudentHobby(
                                student_id=int(student_id), hobby_type_id=int(hid)
                            )
                        )

                db.commit()

                flash("Данные сохранены", "success")

                return redirect(
                    url_for("extracurricular.index", group_id=selected_group_id)
                )

        students_hobbies = {}

        if selected_group_id:

            sig_records = (
                db.query(StudentInGroup)
                .filter_by(group_id=int(selected_group_id))
                .all()
            )

            student_ids = [s.student_id for s in sig_records]

            if student_ids:

                records = (
                    db.query(StudentHobby)
                    .filter(StudentHobby.student_id.in_(student_ids))
                    .all()
                )

                for rec in records:

                    if rec.student_id not in students_hobbies:

                        person = (
                            db.query(Person).filter_by(person_id=rec.student_id).first()
                        )

                        students_hobbies[rec.student_id] = {
                            "person_id": rec.student_id,
                            "full_name": (
                                f"{person.surname} {person.name} {person.patronymic or ''}".strip()
                                if person
                                else "—"
                            ),
                            "hobbies": [],
                        }

                    hobby = (
                        db.query(HobbyType)
                        .filter_by(hobby_type_id=rec.hobby_type_id)
                        .first()
                    )

                    if hobby:

                        students_hobbies[rec.student_id]["hobbies"].append(
                            hobby.hobby_type_name
                        )

        students_table = sorted(students_hobbies.values(), key=lambda x: x["full_name"])

        all_students_for_select = []

        if selected_group_id:

            results = (
                db.query(StudentInGroup, Person)
                .join(Person, StudentInGroup.student_id == Person.person_id)
                .join(Student, StudentInGroup.student_id == Student.person_id)
                .filter(StudentInGroup.group_id == int(selected_group_id))
                .filter(Student.is_expelled == False)
                .all()
            )

            for sig, person in results:

                all_students_for_select.append(
                    {
                        "id": person.person_id,
                        "name": f"{person.surname} {person.name} {person.patronymic or ''}".strip(),
                    }
                )

        all_students_for_select.sort(key=lambda x: x["name"])

        all_hobbies = db.query(HobbyType).order_by(HobbyType.hobby_type_name).all()

        edit_student_id = request.args.get("edit")

        edit_student_name = None

        edit_hobby_ids = []

        if edit_student_id:

            person = db.query(Person).filter_by(person_id=int(edit_student_id)).first()

            if person:

                edit_student_name = (
                    f"{person.surname} {person.name} {person.patronymic or ''}".strip()
                )

            assigned = (
                db.query(StudentHobby).filter_by(student_id=int(edit_student_id)).all()
            )

            edit_hobby_ids = [a.hobby_type_id for a in assigned]

        return render_template(
            "extracurricular.html",
            title="Внеучебная занятость",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            students=students_table,
            all_students_for_select=all_students_for_select,
            all_hobbies=all_hobbies,
            edit_student_id=edit_student_id,
            edit_student_name=edit_student_name,
            edit_hobby_ids=edit_hobby_ids,
        )

    finally:

        db.close()
