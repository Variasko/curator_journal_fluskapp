from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import Role

roles_bp = Blueprint("roles", __name__, url_prefix="/admin/roles")


@roles_bp.route("/", methods=["GET", "POST"])
def manage_roles():

    if "person_id" not in session:

        return redirect(url_for("login"))

    db: Session = SessionLocal()

    try:

        if request.method == "POST":

            action = request.form.get("action")

            if action == "delete":

                role = db.query(Role).get(int(request.form.get("role_id")))

                if role:

                    db.delete(role)

                    db.commit()

                flash("Роль удалена", "success")

                return redirect(url_for("roles.manage_roles"))

            if action in ("add", "edit"):

                name = request.form.get("name", "").strip()

                desc = request.form.get("description", "").strip()

                if not name:

                    flash("Название обязательно", "error")

                    return redirect(url_for("roles.manage_roles"))

                if action == "edit":

                    role = db.query(Role).get(int(request.form.get("role_id")))

                    if role:

                        role.role_name, role.role_description = name, desc or None

                else:

                    db.add(Role(role_name=name, role_description=desc or None))

                db.commit()

                flash("Сохранено", "success")

                return redirect(url_for("roles.manage_roles"))

        items = db.query(Role).all()

        edit_item = None

        if request.args.get("edit"):

            edit_item = db.query(Role).get(int(request.args.get("edit")))

        return render_template(
            "admin_roles.html", title="Роли", items=items, edit_item=edit_item
        )

    finally:

        db.close()
