from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import (
    ClassHour,
    VisitingClassHour,
    Student,
    Person,
    Group,
    StudentInGroup,
)

from utils.formatters import format_group_name

from datetime import datetime, date

class_hours_bp = Blueprint("class_hours", __name__, url_prefix="/class_hours")


@class_hours_bp.route("/", methods=["GET", "POST"])
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

            ch_id = request.form.get("ch_id")

            ch_date_str = request.form.get("ch_date")

            attended_ids = request.form.getlist("attended_ids")

            try:

                ch_date = datetime.strptime(ch_date_str, "%Y-%m-%d").date()

            except (ValueError, TypeError):

                ch_date = date.today()

            if action == "delete" and ch_id:

                db.query(VisitingClassHour).filter_by(class_hour_id=int(ch_id)).delete(
                    synchronize_session=False
                )

                db.query(ClassHour).filter_by(class_hour_id=int(ch_id)).delete(
                    synchronize_session=False
                )

                db.commit()

                flash("Запись удалена", "success")

                return redirect(
                    url_for("class_hours.index", group_id=selected_group_id)
                )

            if action in ("add", "edit"):

                if not ch_date:

                    flash("Укажите дату", "error")

                    return redirect(
                        url_for("class_hours.index", group_id=selected_group_id)
                    )

                sigs = (
                    db.query(StudentInGroup)
                    .filter_by(group_id=int(selected_group_id))
                    .all()
                )

                all_student_ids = [s.student_id for s in sigs]

                if action == "edit":

                    ch = db.query(ClassHour).get(int(ch_id))

                    if ch:

                        ch.class_hour_date = ch_date

                        db.query(VisitingClassHour).filter_by(
                            class_hour_id=ch.class_hour_id
                        ).delete(synchronize_session=False)

                else:

                    ch = ClassHour(
                        class_hour_date=ch_date, group_id=int(selected_group_id)
                    )

                    db.add(ch)

                    db.flush()

                for sid in all_student_ids:

                    is_visited = str(sid) in attended_ids

                    db.add(
                        VisitingClassHour(
                            class_hour_id=ch.class_hour_id,
                            student_id=sid,
                            is_visited=is_visited,
                        )
                    )

                db.commit()

                flash("Сохранено", "success")

                return redirect(
                    url_for("class_hours.index", group_id=selected_group_id)
                )

        class_hours_list = []

        students_for_modal = []

        if selected_group_id:

            raw_ch = (
                db.query(ClassHour).filter_by(group_id=int(selected_group_id)).all()
            )

            for ch in raw_ch:

                count = (
                    db.query(VisitingClassHour)
                    .filter_by(class_hour_id=ch.class_hour_id, is_visited=True)
                    .count()
                )

                class_hours_list.append(
                    {
                        "id": ch.class_hour_id,
                        "date": (
                            ch.class_hour_date.strftime("%d.%m.%Y")
                            if ch.class_hour_date
                            else "—"
                        ),
                        "attended_count": count,
                    }
                )

            results = (
                db.query(StudentInGroup, Person)
                .join(Person, StudentInGroup.student_id == Person.person_id)
                .join(Student, StudentInGroup.student_id == Student.person_id)
                .filter(StudentInGroup.group_id == int(selected_group_id))
                .filter(Student.is_expelled == False)
                .all()
            )

            for sig, person in results:

                students_for_modal.append(
                    {
                        "id": person.person_id,
                        "name": f"{person.surname} {person.name} {person.patronymic or ''}".strip(),
                    }
                )

            students_for_modal.sort(key=lambda x: x["name"])

        class_hours_list.sort(key=lambda x: x["date"], reverse=True)

        edit_id = request.args.get("edit")

        edit_ch = None

        edit_attended_ids = []

        if edit_id:

            edit_ch = db.query(ClassHour).get(int(edit_id))

            if edit_ch:

                visits = (
                    db.query(VisitingClassHour)
                    .filter_by(class_hour_id=edit_ch.class_hour_id, is_visited=True)
                    .all()
                )

                edit_attended_ids = [v.student_id for v in visits]

        return render_template(
            "class_hours.html",
            title="Классные часы",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            class_hours=class_hours_list,
            students_for_modal=students_for_modal,
            edit_ch=edit_ch,
            edit_attended_ids=edit_attended_ids,
            today=today,
        )

    finally:

        db.close()
