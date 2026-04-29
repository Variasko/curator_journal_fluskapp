from flask import (
    Blueprint,
    send_file,
    flash,
    session,
    redirect,
    url_for,
    render_template,
)
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Group
from utils.formatters import format_group_name
from .services.reports import (
    generate_social_passport,
    generate_dormitory_list,
    generate_activists_group,
    generate_extracurricular,
    generate_class_hours_attendance,
    generate_observation_sheet,
    generate_parent_meetings,
    generate_individual_work,
    generate_general_report,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
def index():
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        groups = db.query(Group).filter_by(curator_id=session["person_id"]).all()
        groups_data = [
            {"group_id": g.group_id, "name": format_group_name(g)} for g in groups
        ]
        return render_template("reports.html", title="Отчёты", groups=groups_data)
    finally:
        db.close()


@reports_bp.route("/social-passport/<int:group_id>")
def social_passport(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_social_passport(group_id, db)

        if result:
            output, group_name = result
            filename = f"Социальный_паспорт_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/dormitory/<int:group_id>")
def dormitory(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_dormitory_list(group_id, db)

        if result:
            output, group_name = result
            filename = f"Студенты_в_общежитии_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/activists/<int:group_id>")
def activists(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_activists_group(group_id, db)

        if result:
            output, group_name = result
            filename = f"Активисты_группы_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/extracurricular/<int:group_id>")
def extracurricular(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_extracurricular(group_id, db)

        if result:
            output, group_name = result
            filename = f"Внеучебная_занятость_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/class-hours/<int:group_id>")
def class_hours_attendance(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_class_hours_attendance(group_id, db)

        if result:
            output, group_name = result
            filename = (
                f"Посещаемость_классных_часов_{group_name.replace(' ', '_')}.xlsx"
            )
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/observation-sheet/<int:group_id>")
def observation_sheet(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_observation_sheet(group_id, db)

        if result:
            output, group_name = result
            filename = f"Лист_наблюдений_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/parent-meetings/<int:group_id>")
def parent_meetings_report(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_parent_meetings(group_id, db)

        if result:
            output, group_name = result
            filename = (
                f"Протоколы_родительских_собраний_{group_name.replace(' ', '_')}.xlsx"
            )
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/individual-work/<int:group_id>")
def individual_work(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_individual_work(group_id, db)

        if result:
            output, group_name = result
            filename = f"Индивидуальная_работа_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()


@reports_bp.route("/general/<int:group_id>")
def general_report(group_id):
    if "person_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        group = db.query(Group).filter_by(group_id=group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for("reports.index"))

        if group.curator_id != session["person_id"]:
            flash("Недостаточно прав", "error")
            return redirect(url_for("reports.index"))

        result = generate_general_report(group_id, db)

        if result:
            output, group_name = result
            filename = f"Общий_отчёт_{group_name.replace(' ', '_')}.xlsx"
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=filename,
            )
        else:
            flash("Ошибка генерации отчета", "error")
            return redirect(url_for("reports.index"))
    finally:
        db.close()
