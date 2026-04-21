from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import Student, Person, Group, StudentInGroup

from utils.formatters import format_group_name

from datetime import date

students_bp = Blueprint("students", __name__, url_prefix="/admin/students")


@students_bp.route("/", methods=["GET", "POST"])
def manage_students():

    if "person_id" not in session:

        return redirect(url_for("login"))

    db: Session = SessionLocal()

    try:

        if request.method == "POST":

            action = request.form.get("action")

            if action == "delete":

                person_id = int(request.form.get("person_id"))

                student = (
                    db.query(Student).filter(Student.person_id == person_id).first()
                )

                if student:

                    db.delete(student)

                    db.commit()

                    flash("Запись студента удалена", "success")

                return redirect(url_for("students.manage_students"))

            if action in ("add", "edit"):

                surname = request.form.get("surname", "").strip()

                name = request.form.get("name", "").strip()

                patronymic = request.form.get("patronymic", "").strip()

                passport_serial = request.form.get("passport_serial", "").strip()

                passport_number = request.form.get("passport_number", "").strip()

                phone = request.form.get("phone", "").strip()

                is_expelled = request.form.get("is_expelled") == "on"

                group_id = request.form.get("group_id")

                if not all([surname, name]):

                    flash("Заполните обязательные поля (ФИО)", "error")

                    return redirect(url_for("students.manage_students"))

                person_id = None

                if action == "edit":

                    person_id = int(request.form.get("person_id"))

                    person = (
                        db.query(Person).filter(Person.person_id == person_id).first()
                    )

                    if person:

                        person.surname = surname

                        person.name = name

                        person.patronymic = patronymic or None

                        person.passport_serial = passport_serial or None

                        person.passport_number = passport_number or None

                        person.phone = phone or None

                    student = (
                        db.query(Student).filter(Student.person_id == person_id).first()
                    )

                    if student:

                        student.is_expelled = is_expelled

                else:

                    existing_person = (
                        db.query(Person)
                        .filter(Person.phone == phone, Person.phone.isnot(None))
                        .first()
                    )

                    if existing_person:

                        person_id = existing_person.person_id

                        existing_person.surname = surname

                        existing_person.name = name

                        existing_person.patronymic = patronymic or None

                        existing_person.passport_serial = passport_serial or None

                        existing_person.passport_number = passport_number or None

                    else:

                        new_person = Person(
                            surname=surname,
                            name=name,
                            patronymic=patronymic or None,
                            passport_serial=passport_serial or None,
                            passport_number=passport_number or None,
                            phone=phone or None,
                        )

                        db.add(new_person)

                        db.flush()

                        person_id = new_person.person_id

                    existing_student = (
                        db.query(Student).filter(Student.person_id == person_id).first()
                    )

                    if not existing_student:

                        db.add(Student(person_id=person_id, is_expelled=is_expelled))

                    else:

                        existing_student.is_expelled = is_expelled

                if group_id:

                    gid = int(group_id)

                    sig = (
                        db.query(StudentInGroup)
                        .filter(StudentInGroup.student_id == person_id)
                        .first()
                    )

                    if sig:

                        sig.group_id = gid

                    else:

                        db.add(
                            StudentInGroup(
                                student_id=person_id,
                                group_id=gid,
                                creation_date=date.today(),
                            )
                        )

                db.commit()

                flash(
                    "Данные сохранены" if action == "add" else "Данные обновлены",
                    "success",
                )

                return redirect(url_for("students.manage_students"))

        students = db.query(Student, Person).join(Person).all()

        groups_raw = db.query(Group).all()

        groups_list = [(g.group_id, format_group_name(g)) for g in groups_raw]

        students_list = []

        for student, person in students:

            sig = (
                db.query(StudentInGroup)
                .filter(StudentInGroup.student_id == student.person_id)
                .first()
            )

            if sig and sig.group:

                group_label = format_group_name(sig.group)

            else:

                group_label = "—"

            students_list.append((student, person, group_label))

        edit_id = request.args.get("edit")

        edit_student = None

        edit_person = None

        edit_group_id = None

        if edit_id:

            edit_student = (
                db.query(Student).filter(Student.person_id == int(edit_id)).first()
            )

            if edit_student:

                edit_person = edit_student.person

                sig = (
                    db.query(StudentInGroup)
                    .filter(StudentInGroup.student_id == int(edit_id))
                    .first()
                )

                edit_group_id = sig.group_id if sig else None

        return render_template(
            "admin_students.html",
            title="Студенты",
            students=students_list,
            groups_list=groups_list,
            edit_student=edit_student,
            edit_person=edit_person,
            edit_group_id=edit_group_id,
        )

    finally:

        db.close()
