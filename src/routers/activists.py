from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import (
    PostInGroup,
    PostInGroupType,
    Student,
    Person,
    Group,
    StudentInGroup,
    Course,
    Curator,
)

from utils.formatters import format_group_name

activists_bp = Blueprint("activists", __name__, url_prefix="/activists")


@activists_bp.route("/", methods=["GET", "POST"])
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

            post_id = request.form.get("post_id")

            course_ids = request.form.getlist("course_ids")

            if action == "delete" and student_id and post_id:

                db.query(PostInGroup).filter_by(
                    student_id=int(student_id), post_in_group_type_id=int(post_id)
                ).delete(synchronize_session=False)

                db.commit()

                flash("Запись удалена", "success")

                return redirect(url_for("activists.index", group_id=selected_group_id))

            if action == "save" and student_id and post_id:

                db.query(PostInGroup).filter_by(
                    student_id=int(student_id), post_in_group_type_id=int(post_id)
                ).delete(synchronize_session=False)

                for cid in course_ids:

                    if cid.isdigit():

                        exists = (
                            db.query(PostInGroup)
                            .filter_by(
                                student_id=int(student_id),
                                post_in_group_type_id=int(post_id),
                                course_id=int(cid),
                            )
                            .first()
                        )

                        if not exists:

                            db.add(
                                PostInGroup(
                                    student_id=int(student_id),
                                    post_in_group_type_id=int(post_id),
                                    course_id=int(cid),
                                )
                            )

                db.commit()

                flash("Данные сохранены", "success")

                return redirect(url_for("activists.index", group_id=selected_group_id))

        activists_map = {}

        if selected_group_id:

            group_students = (
                db.query(StudentInGroup)
                .filter_by(group_id=int(selected_group_id))
                .all()
            )

            student_ids = [s.student_id for s in group_students]

            if student_ids:

                records = (
                    db.query(PostInGroup)
                    .filter(PostInGroup.student_id.in_(student_ids))
                    .all()
                )

                for rec in records:

                    key = (rec.student_id, rec.post_in_group_type_id)

                    if key not in activists_map:

                        person = (
                            db.query(Person).filter_by(person_id=rec.student_id).first()
                        )

                        post_type = (
                            db.query(PostInGroupType)
                            .filter_by(post_in_group_type_id=rec.post_in_group_type_id)
                            .first()
                        )

                        activists_map[key] = {
                            "student_id": rec.student_id,
                            "post_id": rec.post_in_group_type_id,
                            "full_name": (
                                f"{person.surname} {person.name} {person.patronymic or ''}".strip()
                                if person
                                else "—"
                            ),
                            "post_name": (
                                post_type.post_in_group_type_name if post_type else "—"
                            ),
                            "courses": [],
                        }

                    activists_map[key]["courses"].append(rec.course_id)

        activists_list = sorted(activists_map.values(), key=lambda x: x["full_name"])

        all_posts = db.query(PostInGroupType).all()

        all_courses = db.query(Course).order_by(Course.course_id).all()

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

        edit_student_id = request.args.get("edit_student")

        edit_post_id = request.args.get("edit_post")

        edit_student_name = None

        edit_courses = []

        if edit_student_id and edit_post_id:

            person = db.query(Person).filter_by(person_id=int(edit_student_id)).first()

            if person:

                edit_student_name = (
                    f"{person.surname} {person.name} {person.patronymic or ''}".strip()
                )

            current_recs = (
                db.query(PostInGroup)
                .filter_by(
                    student_id=int(edit_student_id),
                    post_in_group_type_id=int(edit_post_id),
                )
                .all()
            )

            edit_courses = [r.course_id for r in current_recs]

        return render_template(
            "activists.html",
            title="Активисты группы",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            activists=activists_list,
            all_posts=all_posts,
            all_courses=all_courses,
            students_list=students_list,
            edit_student_id=edit_student_id,
            edit_post_id=edit_post_id,
            edit_student_name=edit_student_name,
            edit_courses=edit_courses,
        )

    finally:

        db.close()
