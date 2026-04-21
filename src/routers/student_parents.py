from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import StudentParent, Student, Parent, Person

student_parents_bp = Blueprint(
    "student_parents", __name__, url_prefix="/admin/student-parents"
)


@student_parents_bp.route("/", methods=["GET", "POST"])
def manage_student_parents():

    if "person_id" not in session:

        return redirect(url_for("login"))

    db: Session = SessionLocal()

    try:

        if request.method == "POST":

            action = request.form.get("action")

            if action == "delete":

                sid = int(request.form.get("student_id"))

                pid = int(request.form.get("parent_id"))

                link = (
                    db.query(StudentParent)
                    .filter_by(student_id=sid, parent_id=pid)
                    .first()
                )

                if link:

                    db.delete(link)

                    db.commit()

                flash("Связь удалена", "success")

                return redirect(url_for("student_parents.manage_student_parents"))

            if action == "add":

                sid = int(request.form.get("student_id"))

                pid = int(request.form.get("parent_id"))

                if not sid or not pid:

                    flash("Выберите студента и родителя", "error")

                    return redirect(url_for("student_parents.manage_student_parents"))

                if (
                    db.query(StudentParent)
                    .filter_by(student_id=sid, parent_id=pid)
                    .first()
                ):

                    flash("Такая связь уже существует", "error")

                    return redirect(url_for("student_parents.manage_student_parents"))

                db.add(StudentParent(student_id=sid, parent_id=pid))

                db.commit()

                flash("Связь добавлена", "success")

                return redirect(url_for("student_parents.manage_student_parents"))

        links = db.query(StudentParent).all()

        students = db.query(Student).join(Person).all()

        parents = db.query(Parent).all()

        table_data = []

        for link in links:

            student = (
                db.query(Student)
                .join(Person)
                .filter(Student.person_id == link.student_id)
                .first()
            )

            parent = db.query(Parent).filter(Parent.parent_id == link.parent_id).first()

            if student and parent:

                s_name = f"{student.person.surname} {student.person.name}"

                p_name = f"{parent.surname} {parent.name}"

                table_data.append(
                    {
                        "student_id": link.student_id,
                        "parent_id": link.parent_id,
                        "s_name": s_name,
                        "p_name": p_name,
                    }
                )

        return render_template(
            "admin_student_parents.html",
            title="Родители студентов",
            table_data=table_data,
            students=students,
            parents=parents,
        )

    finally:

        db.close()
