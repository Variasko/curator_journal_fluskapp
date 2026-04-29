from functools import wraps
from flask import (
    Blueprint,
    send_file,
    flash,
    session,
    redirect,
    url_for,
    render_template,
    request,
)
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Group
from utils.formatters import format_group_name
from utilities import login_required
from reports import (
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
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def curator_required(f):
    """Декоратор: авторизация + проверка, что пользователь куратор группы."""
    @wraps(f)
    def wrapper(group_id, *args, **kwargs):
        if "person_id" not in session:
            flash("Для доступа к странице необходимо авторизоваться", "warning")
            return redirect(url_for("login", next=request.url))

        db: Session = SessionLocal()
        try:
            if session.get("person_role") != 3:
                group = db.query(Group).filter_by(group_id=group_id).first()
            else:
                group = db.query(Group).first()

            if not group:
                flash("Группа не найдена", "error")
                return redirect(url_for("reports.index"))

            if group.curator_id != session["person_id"] and session["person_role"] != 3:
                flash("Недостаточно прав для этой группы", "error")
                print("Недостаточно прав для этой группы")
                return redirect(url_for("reports.index"))
            
            return f(group_id, db, *args, **kwargs)
        finally:
            db.close()
    return wrapper


def _send_excel(group_id: int, generator, filename_template: str, db: Session):
    """Единый хелпер генерации и отдачи Excel."""
    result = generator(group_id, db)
    if result:
        output, group_name = result
        safe_name = group_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = filename_template.format(safe_name)
        return send_file(
            output,
            mimetype=XLSX_MIME,
            as_attachment=True,
            download_name=filename,
        )
    flash("Ошибка генерации отчёта или данные отсутствуют", "error")
    return redirect(url_for("reports.index"))


@reports_bp.route("/")
@login_required
def index():
    db: Session = SessionLocal()
    try:
        groups = db.query(Group).filter_by(curator_id=session["person_id"]).all()
        
        if session.get("person_role") != 3:
            groups_data = [
                {"group_id": g.group_id, "display_name": format_group_name(g)}
                for g in groups
            ]
        else:
                groups_data = [
                {"group_id": g.group_id, "display_name": format_group_name(g)}
                for g in db.query(Group).all()
            ]

        return render_template("reports.html", title="Отчёты", groups=groups_data)
    finally:
        db.close()


@reports_bp.route("/social-passport/<int:group_id>")
@curator_required
def social_passport(group_id, db):
    return _send_excel(group_id, generate_social_passport, "Социальный_паспорт_{}.xlsx", db)


@reports_bp.route("/dormitory/<int:group_id>")
@curator_required
def dormitory(group_id, db):
    return _send_excel(group_id, generate_dormitory_list, "Студенты_в_общежитии_{}.xlsx", db)


@reports_bp.route("/activists/<int:group_id>")
@curator_required
def activists(group_id, db):
    return _send_excel(group_id, generate_activists_group, "Активисты_группы_{}.xlsx", db)


@reports_bp.route("/extracurricular/<int:group_id>")
@curator_required
def extracurricular(group_id, db):
    return _send_excel(group_id, generate_extracurricular, "Внеучебная_занятость_{}.xlsx", db)


@reports_bp.route("/class-hours/<int:group_id>")
@curator_required
def class_hours_attendance(group_id, db):
    return _send_excel(group_id, generate_class_hours_attendance, "Посещаемость_классных_часов_{}.xlsx", db)


@reports_bp.route("/observation-sheet/<int:group_id>")
@curator_required
def observation_sheet(group_id, db):
    return _send_excel(group_id, generate_observation_sheet, "Лист_наблюдений_{}.xlsx", db)


@reports_bp.route("/parent-meetings/<int:group_id>")
@curator_required
def parent_meetings_report(group_id, db):
    return _send_excel(group_id, generate_parent_meetings, "Протоколы_родительских_собраний_{}.xlsx", db)


@reports_bp.route("/individual-work/<int:group_id>")
@curator_required
def individual_work(group_id, db):
    return _send_excel(group_id, generate_individual_work, "Индивидуальная_работа_{}.xlsx", db)


@reports_bp.route("/general/<int:group_id>")
@curator_required
def general_report(group_id, db):
    return _send_excel(group_id, generate_general_report, "Общий_отчёт_{}.xlsx", db)