from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import Curator, Person, Role

from werkzeug.security import generate_password_hash

curators_bp = Blueprint("curators", __name__, url_prefix="/admin/curators")


@curators_bp.route("/", methods=["GET", "POST"])
def manage_curators():

    if "person_id" not in session:

        return redirect(url_for("login"))

    db: Session = SessionLocal()

    try:

        if request.method == "POST":

            action = request.form.get("action")

            if action == "delete":

                person_id = int(request.form.get("person_id"))

                curator = (
                    db.query(Curator).filter(Curator.person_id == person_id).first()
                )

                if curator:

                    db.delete(curator)

                    db.commit()

                    flash("Куратор удалён", "success")

                return redirect(url_for("curators.manage_curators"))

            if action in ("add", "edit"):

                surname = request.form.get("surname", "").strip()

                name = request.form.get("name", "").strip()

                patronymic = request.form.get("patronymic", "").strip()

                passport_serial = request.form.get("passport_serial", "").strip()

                passport_number = request.form.get("passport_number", "").strip()

                phone = request.form.get("phone", "").strip()

                login = request.form.get("login", "").strip()

                password = request.form.get("password", "")

                role_id = int(request.form.get("role_id"))

                if not all([surname, name, login]):

                    flash("Заполните обязательные поля (ФИО, Логин)", "error")

                    return redirect(url_for("curators.manage_curators"))

                person_id = None

                if action == "edit":

                    person_id = int(request.form.get("person_id"))

                    person = db.query(Person).get(person_id)

                    if person:

                        person.surname = surname

                        person.name = name

                        person.patronymic = patronymic or None

                        person.passport_serial = passport_serial or None

                        person.passport_number = passport_number or None

                        person.phone = phone or None

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

                    new_curator = Curator(
                        person_id=person_id,
                        login=login,
                        password_hash=generate_password_hash(password),
                        role_id=role_id,
                    )

                    db.add(new_curator)

                if action == "edit":

                    curator = (
                        db.query(Curator).filter(Curator.person_id == person_id).first()
                    )

                    if curator:

                        curator.login = login

                        curator.role_id = role_id

                        if password:

                            curator.password_hash = generate_password_hash(password)

                db.commit()

                flash("Данные сохранены", "success")

                return redirect(url_for("curators.manage_curators"))

        curators = db.query(Curator).all()

        roles = db.query(Role).all()

        edit_curator = None

        edit_person = None

        edit_id = request.args.get("edit")

        if edit_id:

            edit_curator = (
                db.query(Curator).filter(Curator.person_id == int(edit_id)).first()
            )

            if edit_curator:

                edit_person = edit_curator.person

        return render_template(
            "admin_curators.html",
            title="Кураторы",
            curators=curators,
            roles=roles,
            edit_curator=edit_curator,
            edit_person=edit_person,
        )

    finally:

        db.close()
