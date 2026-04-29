from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import (
    SocialPassport,
    Student,
    Person,
    SocialStatus,
    Group,
    StudentInGroup,
    Curator,
)

from utils.formatters import format_group_name

social_bp = Blueprint("social", __name__, url_prefix="/social_passport")


@social_bp.route("/", methods=["GET", "POST"])
def index():

    if "person_id" not in session:

        return redirect(url_for("login"))

    curator_id = session["person_id"]

    db: Session = SessionLocal()

    try:

        curator_groups = db.query(Group).filter_by(curator_id=curator_id).all()

        if session.get("person_role") != 3:
            groups_data = [
                {"group_id": g.group_id, "display_name": format_group_name(g)}
                for g in curator_groups
            ]
        else:
                groups_data = [
                {"group_id": g.group_id, "display_name": format_group_name(g)}
                for g in db.query(Group).all()
            ]

        selected_group_id = request.args.get("group_id") or request.form.get("group_id")

        if not selected_group_id and groups_data:

            selected_group_id = groups_data[0]["group_id"]

        if request.method == "POST":

            action = request.form.get("action")

            student_id = request.form.get("student_id")

            status_ids = request.form.getlist("status_ids")

            if action == "delete" and student_id:

                db.query(SocialPassport).filter_by(student_id=int(student_id)).delete()

                db.commit()

                flash("Статусы удалены", "success")

                return redirect(url_for("social.index", group_id=selected_group_id))

            if action == "save" and student_id:

                db.query(SocialPassport).filter_by(student_id=int(student_id)).delete()

                for sid in status_ids:

                    if sid.isdigit():

                        db.add(
                            SocialPassport(
                                student_id=int(student_id), social_status_id=int(sid)
                            )
                        )

                db.commit()

                flash("Данные сохранены", "success")

                return redirect(url_for("social.index", group_id=selected_group_id))

        students_data = []

        if selected_group_id:

            sig_records = (
                db.query(StudentInGroup)
                .filter_by(group_id=int(selected_group_id))
                .all()
            )

            for sig in sig_records:

                student = (
                    db.query(Student)
                    .join(Person)
                    .filter(Student.person_id == sig.student_id)
                    .first()
                )

                if student and not student.is_expelled:

                    assigned = (
                        db.query(SocialPassport, SocialStatus)
                        .join(SocialStatus)
                        .filter(SocialPassport.student_id == student.person_id)
                        .all()
                    )

                    status_list = [sp.SocialStatus.status_name for sp in assigned]

                    students_data.append(
                        {
                            "person_id": student.person_id,
                            "full_name": f"{student.person.surname} {student.person.name} {student.person.patronymic or ''}".strip(),
                            "statuses": status_list,
                        }
                    )

        all_statuses = db.query(SocialStatus).all()

        edit_student_id = request.args.get("edit")

        edit_student_name = None

        edit_assigned_ids = []

        if edit_student_id:

            student = (
                db.query(Student)
                .join(Person)
                .filter(Student.person_id == int(edit_student_id))
                .first()
            )

            if student:

                edit_student_name = f"{student.person.surname} {student.person.name} {student.person.patronymic or ''}".strip()

                assigned = (
                    db.query(SocialPassport)
                    .filter_by(student_id=int(edit_student_id))
                    .all()
                )

                edit_assigned_ids = [a.social_status_id for a in assigned]

        return render_template(
            "social_passport.html",
            title="Социальный паспорт группы",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            students=students_data,
            all_statuses=all_statuses,
            edit_student_id=edit_student_id,
            edit_student_name=edit_student_name,
            edit_assigned_ids=edit_assigned_ids,
        )

    finally:

        db.close()
