from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
)

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import (
    Person,
    Curator,
    Group,
    StudentInGroup,
    ObservationList,
    ClassHour,
)

import io

profile_bp = Blueprint("profile", __name__, url_prefix="")


@profile_bp.route("/", methods=["GET", "POST"])
@profile_bp.route("/profile", methods=["GET", "POST"])
def index():

    if "person_id" not in session:

        return redirect(url_for("login"))

    person_id = session["person_id"]

    db: Session = SessionLocal()

    try:

        person = db.query(Person).filter_by(person_id=person_id).first()

        curator = db.query(Curator).filter_by(person_id=person_id).first()

        if request.method == "POST":

            action = request.form.get("action")

            if action == "update_info":

                person.surname = request.form.get("surname", "").strip()

                person.name = request.form.get("name", "").strip()

                person.patronymic = request.form.get("patronymic", "").strip() or None

                person.phone = request.form.get("phone", "").strip() or None

                if "avatar" in request.files:

                    file = request.files["avatar"]

                    if (
                        file
                        and file.filename != ""
                        and file.content_type.startswith("image/")
                    ):

                        person.photo = file.read()

                db.commit()

                flash("Профиль обновлён", "success")

                return redirect(url_for("profile.index"))

        groups = db.query(Group).filter_by(curator_id=person_id).all()

        group_ids = [g.group_id for g in groups]

        student_ids_in_groups = (
            db.query(StudentInGroup.student_id)
            .filter(StudentInGroup.group_id.in_(group_ids))
            .all()
        )

        student_ids_list = [s[0] for s in student_ids_in_groups]

        stats = {
            "groups": len(groups),
            "students": len(student_ids_list),
            "observations": (
                db.query(ObservationList)
                .filter(ObservationList.student_id.in_(student_ids_list))
                .count()
                if student_ids_list
                else 0
            ),
            "class_hours": (
                db.query(ClassHour).filter(ClassHour.group_id.in_(group_ids)).count()
                if group_ids
                else 0
            ),
        }

        return render_template(
            "index.html",
            title="Профиль куратора",
            person=person,
            curator=curator,
            stats=stats,
        )

    finally:

        db.close()


@profile_bp.route("/avatar/<int:person_id>")
def get_avatar(person_id):

    db: Session = SessionLocal()

    try:

        person = db.query(Person).filter_by(person_id=person_id).first()

        if person and person.photo:

            return send_file(io.BytesIO(person.photo), mimetype="image/jpeg")

        return redirect(url_for("static", filename="img/default_avatar.jpg"))

    finally:

        db.close()
