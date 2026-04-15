from flask import Flask, request, redirect, url_for, session, flash, render_template
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import timedelta

from database.models import Curator
from database.database import SessionLocal, init_db
from utils import login_required, verify_password
from config.config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

@app.route('/')
@app.route('/profile')
@login_required
def index():
    return render_template("index.html", title="Профиль")

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

            
            if not curator or not verify_password(password_input, curator.password_hash):
                flash("Неверный логин или пароль", "error")
                return render_template("login.html")

            session["person_id"] = curator.person_id
            session["person_role"] = curator.role_id
            session.permanent = True

            
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        finally:
            db.close()

    return render_template("login.html")

@app.route('/social_passport')
def social_passport():
    return render_template("social_passport.html", title="Социальный паспорт группы")

@app.route('/activists')
def activists():
    return render_template("activists.html", title="Активисты группы")

@app.route('/dormitory')
def dormitory():
    return render_template("dormitory.html", title="Студенты в общежитии")

@app.route('/meetings')
def meetings():
    return render_template("meetings.html", title="Родительские собрания")

@app.route('/individual_work')
def individual_work():
    return render_template("individual_work.html", title="Индивидуальная работа")

@app.route('/extracurricular')
def extracurricular():
    return render_template("extracurricular.html", title="Внеучебная занятость")

@app.route('/class_hours')
def class_hours():
    return render_template("class_hours.html", title="Классные часы")

@app.route('/observation_sheet')
def observation_sheet():
    return render_template("observation_sheet.html", title="Лист наблюдеиния")

@app.route('/report')
def report():
    return render_template("report.html", title="Отчёты")

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Вы успешно вышли из системы", "success")
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    app.run(host="192.168.1.17", debug=True)