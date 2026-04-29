from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)

import io

import csv

from database.database import SessionLocal

from utils.csv_handler import detect_table_type, parse_csv, import_data

import_bp = Blueprint("import_data", __name__, url_prefix="/admin/import")


TEMPLATES = {
    "curators": ["surname", "name", "patronymic", "phone", "login", "password", "role_name"],
    "students": ["surname", "name", "patronymic", "phone", "group_name"],
    "roles": ["role_name", "description"],
    "parents": ["surname", "name", "patronymic", "phone"],
    "hobbies": ["hobby_type_name"],
    "posts": ["post_in_group_type_name"],
    "statuses": ["status_name"],
}


@import_bp.route("/")
def import_page():

    return render_template(
        "admin_import.html", title="Импорт данных", templates=TEMPLATES
    )


@import_bp.route("/template/<table_type>")
def download_template(table_type):

    if table_type not in TEMPLATES:

        flash("Шаблон не найден", "error")

        return redirect(url_for("import_data.import_page"))

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(TEMPLATES[table_type])

    writer.writerow([""] * len(TEMPLATES[table_type]))

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{table_type}_template.csv",
    )


@import_bp.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        flash("Файл не выбран", "error")
        return redirect(url_for("import_data.import_page"))

    file = request.files["file"]
    if file.filename == "":
        flash("Файл не выбран", "error")
        return redirect(url_for("import_data.import_page"))

    db = SessionLocal()
    try:
        data = parse_csv(file.stream)
        if not data:
            flash("Файл пуст или некорректен", "error")
            return redirect(url_for("import_data.import_page"))

        table_type = detect_table_type(list(data[0].keys()))
        if not table_type:
            flash(f'Не удалось определить тип. Заголовки: {", ".join(data[0].keys())}', "error")
            return redirect(url_for("import_data.import_page"))

        result = import_data(db, table_type, data)

        return render_template(
            "admin_import.html",
            title="Импорт данных",
            templates=TEMPLATES,
            import_result=result,
            table_type=table_type
        )
    except Exception as e:
        db.rollback()
        import traceback; traceback.print_exc()
        flash(f"Ошибка при обработке: {str(e)}", "error")
        return redirect(url_for("import_data.import_page"))
    finally:
        db.close()