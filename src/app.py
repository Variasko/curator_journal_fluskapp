import os
from flask import Flask, request, redirect, url_for, session, flash, render_template
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import timedelta

from database.models import Curator
from database.database import SessionLocal, init_db_with_admin
from utilities import login_required, verify_password, admin_required
from utils.seed import run_seed
from config.config import SECRET_KEY, DB_URL, is_debug, is_first_run
from routers import get_blueprints

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

for bp in get_blueprints():
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

            if not curator or not verify_password(password_input, curator.password_hash):
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


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html", title="Страница не найдена"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html", title="Ошибка сервера"), 500


if __name__ == "__main__":
    if is_first_run(DB_URL):
        print("Первый запуск: инициализация БД и создание администратора...")
        init_db_with_admin()
        run_seed()
        print("Готово! Логин: admin, Пароль: admin (смените после входа!)")

    debug_mode = is_debug()
    print(f"Запуск приложения в режиме: {'ОТЛАДКА' if debug_mode else 'ПРОДАКШН'}")
    
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)