from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import (
    StudentIndividualWork,
    ParentIndividualWork,
    Student,
    Parent,
    Person,
    Group,
    StudentInGroup,
    StudentParent,
    Curator,
)

from utils.formatters import format_group_name

from datetime import datetime, date

indiv_bp = Blueprint("individual_work", __name__, url_prefix="/individual_work")


@indiv_bp.route("/", methods=["GET", "POST"])
def index():

    if "person_id" not in session:

        return redirect(url_for("login"))

    curator_id = session["person_id"]

    db: Session = SessionLocal()

    today = date.today().isoformat()

    try:

        curator_groups = db.query(Group).filter_by(curator_id=curator_id).all()

        groups_data = [
            {"group_id": g.group_id, "display_name": format_group_name(g)}
            for g in curator_groups
        ]

        selected_group_id = request.args.get("group_id") or request.form.get("group_id")

        if not selected_group_id and groups_data:

            selected_group_id = groups_data[0]["group_id"]

        work_type = request.args.get("type") or request.form.get("type") or "students"

        if request.method == "POST":

            action = request.form.get("action")

            rec_id = request.form.get("record_id")

            target_id = request.form.get("target_id")

            work_date_str = request.form.get("work_date")

            topic = request.form.get("topic", "").strip()

            result = request.form.get("result", "").strip()

            try:

                work_date = datetime.strptime(work_date_str, "%Y-%m-%d").date()

            except:

                work_date = date.today()

            if action == "delete" and rec_id:

                if work_type == "students":

                    db.query(StudentIndividualWork).filter_by(
                        student_individual_work_id=int(rec_id)
                    ).delete()

                else:

                    db.query(ParentIndividualWork).filter_by(
                        parent_individual_work_id=int(rec_id)
                    ).delete()

                db.commit()

                flash("Запись удалена", "success")

                return redirect(
                    url_for(
                        "individual_work.index",
                        group_id=selected_group_id,
                        type=work_type,
                    )
                )

            if action in ("add", "edit"):

                if not target_id or not topic:

                    flash("Заполните обязательные поля", "error")

                    return redirect(
                        url_for(
                            "individual_work.index",
                            group_id=selected_group_id,
                            type=work_type,
                        )
                    )

                if work_type == "students":

                    if action == "edit":

                        rec = db.query(StudentIndividualWork).get(int(rec_id))

                        if rec:

                            rec.student_id, rec.date, rec.topic, rec.result = (
                                int(target_id),
                                work_date,
                                topic,
                                result or None,
                            )

                    else:

                        db.add(
                            StudentIndividualWork(
                                student_id=int(target_id),
                                date=work_date,
                                topic=topic,
                                result=result or None,
                            )
                        )

                else:

                    if action == "edit":

                        rec = db.query(ParentIndividualWork).get(int(rec_id))

                        if rec:

                            rec.parent_id, rec.date, rec.topic, rec.result = (
                                int(target_id),
                                work_date,
                                topic,
                                result or None,
                            )

                    else:

                        db.add(
                            ParentIndividualWork(
                                parent_id=int(target_id),
                                date=work_date,
                                topic=topic,
                                result=result or None,
                            )
                        )

                db.commit()

                flash("Сохранено", "success")

                return redirect(
                    url_for(
                        "individual_work.index",
                        group_id=selected_group_id,
                        type=work_type,
                    )
                )

        records = []

        targets_for_select = []

        if selected_group_id:

            gid = int(selected_group_id)

            group_student_ids = [
                s.student_id
                for s in db.query(StudentInGroup).filter_by(group_id=gid).all()
            ]

            if work_type == "students":

                if group_student_ids:

                    raw_recs = (
                        db.query(StudentIndividualWork)
                        .filter(StudentIndividualWork.student_id.in_(group_student_ids))
                        .all()
                    )

                    for r in raw_recs:

                        p = db.query(Person).filter_by(person_id=r.student_id).first()

                        records.append(
                            {
                                "id": r.student_individual_work_id,
                                "date": r.date.strftime("%d.%m.%Y") if r.date else "—",
                                "name": (
                                    f"{p.surname} {p.name} {p.patronymic or ''}".strip()
                                    if p
                                    else "—"
                                ),
                                "topic": r.topic,
                                "result": r.result or "—",
                            }
                        )

                for sid in group_student_ids:

                    p = db.query(Person).filter_by(person_id=sid).first()

                    if p:

                        targets_for_select.append(
                            {"id": sid, "name": f"{p.surname} {p.name}"}
                        )

            else:

                if group_student_ids:

                    parent_links = (
                        db.query(StudentParent)
                        .filter(StudentParent.student_id.in_(group_student_ids))
                        .all()
                    )

                    parent_ids = list(set([pl.parent_id for pl in parent_links]))

                    if parent_ids:

                        raw_recs = (
                            db.query(ParentIndividualWork)
                            .filter(ParentIndividualWork.parent_id.in_(parent_ids))
                            .all()
                        )

                        for r in raw_recs:

                            par = (
                                db.query(Parent)
                                .filter_by(parent_id=r.parent_id)
                                .first()
                            )

                            records.append(
                                {
                                    "id": r.parent_individual_work_id,
                                    "date": (
                                        r.date.strftime("%d.%m.%Y") if r.date else "—"
                                    ),
                                    "name": (
                                        f"{par.surname} {par.name} {par.patronymic or ''}".strip()
                                        if par
                                        else "—"
                                    ),
                                    "topic": r.topic,
                                    "result": r.result or "—",
                                }
                            )

                if group_student_ids:

                    parent_ids = list(
                        set(
                            [
                                pl.parent_id
                                for pl in db.query(StudentParent)
                                .filter(StudentParent.student_id.in_(group_student_ids))
                                .all()
                            ]
                        )
                    )

                    for pid in parent_ids:

                        par = db.query(Parent).filter_by(parent_id=pid).first()

                        if par:

                            targets_for_select.append(
                                {"id": pid, "name": f"{par.surname} {par.name}"}
                            )

        records.sort(key=lambda x: x["date"], reverse=True)

        targets_for_select.sort(key=lambda x: x["name"])

        edit_id = request.args.get("edit")

        edit_rec = None

        if edit_id:

            edit_rec = (
                db.query(StudentIndividualWork).get(int(edit_id))
                if work_type == "students"
                else db.query(ParentIndividualWork).get(int(edit_id))
            )

        return render_template(
            "individual_work.html",
            title="Индивидуальная работа",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            work_type=work_type,
            records=records,
            targets_for_select=targets_for_select,
            edit_rec=edit_rec,
            today=today,
        )

    finally:

        db.close()
