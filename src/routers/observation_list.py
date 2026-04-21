from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import ObservationList, Student, Person, Group, StudentInGroup

from utils.formatters import format_group_name

from datetime import date, datetime

observation_bp = Blueprint("observation", __name__, url_prefix="/observation_sheet")


@observation_bp.route("/", methods=["GET", "POST"])
def index():

    if "person_id" not in session:

        return redirect(url_for("login"))

    curator_id = session["person_id"]

    db: Session = SessionLocal()

    today = date.today().isoformat()

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

            record_id = request.form.get("record_id")

            student_id = request.form.get("student_id")

            characteristic = request.form.get("characteristic", "").strip()

            raw_date = request.form.get("observation_date")

            if raw_date:

                try:

                    obs_date = datetime.strptime(raw_date, "%Y-%m-%d").date()

                except ValueError:

                    obs_date = date.today()

            else:

                obs_date = date.today()

            if action == "delete" and record_id:

                db.query(ObservationList).filter_by(
                    observation_list_id=int(record_id)
                ).delete()

                db.commit()

                flash("Запись удалена", "success")

                return redirect(
                    url_for("observation.index", group_id=selected_group_id)
                )

            if action in ("add", "edit"):

                if not student_id or not characteristic:

                    flash("Заполните студента и характеристику", "error")

                    return redirect(
                        url_for("observation.index", group_id=selected_group_id)
                    )

                if action == "edit":

                    rec = db.query(ObservationList).get(int(record_id))

                    if rec:

                        rec.student_id = int(student_id)

                        rec.characteristic = characteristic

                        rec.observation_date = obs_date

                else:

                    db.add(
                        ObservationList(
                            student_id=int(student_id),
                            characteristic=characteristic,
                            observation_date=obs_date,
                        )
                    )

                db.commit()

                flash("Сохранено", "success")

                return redirect(
                    url_for("observation.index", group_id=selected_group_id)
                )

        observations = []

        if selected_group_id:

            sigs = (
                db.query(StudentInGroup)
                .filter_by(group_id=int(selected_group_id))
                .all()
            )

            student_ids = [s.student_id for s in sigs]

            if student_ids:

                recs = (
                    db.query(ObservationList)
                    .filter(ObservationList.student_id.in_(student_ids))
                    .all()
                )

                for rec in recs:

                    person = (
                        db.query(Person).filter_by(person_id=rec.student_id).first()
                    )

                    observations.append(
                        {
                            "id": rec.observation_list_id,
                            "student_id": rec.student_id,
                            "student_name": (
                                f"{person.surname} {person.name} {person.patronymic or ''}".strip()
                                if person
                                else "—"
                            ),
                            "date": (
                                rec.observation_date.strftime("%d.%m.%Y")
                                if rec.observation_date
                                else "—"
                            ),
                            "characteristic": rec.characteristic,
                        }
                    )

            observations.sort(key=lambda x: x["date"], reverse=True)

        students_list = []

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

                students_list.append(
                    {
                        "id": person.person_id,
                        "name": f"{person.surname} {person.name} {person.patronymic or ''}".strip(),
                    }
                )

            students_list.sort(key=lambda x: x["name"])

        edit_id = request.args.get("edit")

        edit_rec = None

        if edit_id:

            edit_rec = db.query(ObservationList).get(int(edit_id))

        return render_template(
            "observation_list.html",
            title="Лист наблюдений куратора",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            observations=observations,
            students_list=students_list,
            edit_rec=edit_rec,
            today=today,
        )

    finally:

        db.close()
