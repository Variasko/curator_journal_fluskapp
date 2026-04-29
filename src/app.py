from flask import Flask, request, redirect, url_for, session, flash, render_template

from sqlalchemy import select

from sqlalchemy.orm import Session

from datetime import timedelta


from database.models import Curator

from database.database import SessionLocal

from utilities import login_required, verify_password, admin_required

from config.config import SECRET_KEY

from routers import (
    profile_bp,
    curators_bp,
    students_bp,
    groups_bp,
    specs_bp,
    quals_bp,
    roles_bp,
    parents_bp,
    student_parents_bp,
    statuses_bp,
    posts_bp,
    hobbies_bp,
    import_bp,
    social_bp,
    activists_bp,
    dormitory_bp,
    extracurricular_bp,
    observation_bp,
    parent_meetings_bp,
    indiv_bp,
    class_hours_bp,
    reports_bp,
)

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)


blueprints = [
    profile_bp,
    curators_bp,
    students_bp,
    groups_bp,
    specs_bp,
    quals_bp,
    roles_bp,
    parents_bp,
    student_parents_bp,
    statuses_bp,
    posts_bp,
    hobbies_bp,
    import_bp,
    social_bp,
    activists_bp,
    dormitory_bp,
    extracurricular_bp,
    observation_bp,
    parent_meetings_bp,
    indiv_bp,
    class_hours_bp,
    reports_bp,
]


for bp in blueprints:

    app.register_blueprint(bp)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_input = request.form.get("login", "").strip()

        password_input = request.form.get("password", "")

        if not login_input or not password_input:

            flash("Заполните все поля", "error")

            return render_template("login.html")

        db: Session = SessionLocal()

        try:

            stmt = select(Curator).where(Curator.login == login_input)

            curator = db.scalar(stmt)

            if not curator or not verify_password(
                password_input, curator.password_hash
            ):

                flash("Неверный логин или пароль", "error")

                return render_template("login.html")

            session["person_id"] = curator.person_id

            session["person_role"] = curator.role_id

            session.permanent = True

            next_page = request.args.get("next")

            return redirect(next_page or url_for("profile.index"))

        finally:

            db.close()

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash("Вы успешно вышли из системы", "success")

    return redirect(url_for("login"))


@app.route("/adminpanel")
@login_required
@admin_required
def adminpanel():

    return render_template("admin_panel.html", title="Администрирование")


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
