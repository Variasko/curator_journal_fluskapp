from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from sqlalchemy.orm import Session

from database.database import SessionLocal

from database.models import ParentMeeting, Group

from utils.formatters import format_group_name

from datetime import datetime, date

parent_meetings_bp = Blueprint(
    "parent_meetings", __name__, url_prefix="/parent_meetings"
)


@parent_meetings_bp.route("/", methods=["GET", "POST"])
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

        if request.method == "POST":

            action = request.form.get("action")

            meeting_id = request.form.get("meeting_id")

            meeting_date_str = request.form.get("meeting_date")

            invited = request.form.get("invited", "").strip()

            visited_count = int(request.form.get("visited_count", 0))

            unvisited_count = int(request.form.get("unvisited_count", 0))

            excused_count = int(request.form.get("excused_count", 0))

            topics = request.form.get("topics", "").strip()

            speakers = request.form.get("speakers", "").strip()

            resolution = request.form.get("resolution", "").strip()

            try:

                meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d").date()

            except (ValueError, TypeError):

                meeting_date = date.today()

            if action == "delete" and meeting_id:

                db.query(ParentMeeting).filter_by(
                    parent_meeting_id=int(meeting_id)
                ).delete()

                db.commit()

                flash("Протокол удалён", "success")

                return redirect(
                    url_for("parent_meetings.index", group_id=selected_group_id)
                )

            if action in ("add", "edit"):

                if not topics:

                    flash("Укажите тему собрания", "error")

                    return redirect(
                        url_for("parent_meetings.index", group_id=selected_group_id)
                    )

                if action == "edit":

                    meeting = db.query(ParentMeeting).get(int(meeting_id))

                    if meeting:

                        meeting.meeting_date = meeting_date

                        meeting.invited = invited or None

                        meeting.visited_count = visited_count

                        meeting.unvisited = unvisited_count

                        meeting.excused_count = excused_count

                        meeting.topics = topics or None

                        meeting.speakers = speakers or None

                        meeting.meeting_result = resolution or None

                else:

                    db.add(
                        ParentMeeting(
                            group_id=int(selected_group_id),
                            curator_id=curator_id,
                            meeting_date=meeting_date,
                            invited=invited or None,
                            visited_count=visited_count,
                            unvisited=unvisited_count,
                            excused_count=excused_count,
                            topics=topics or None,
                            speakers=speakers or None,
                            meeting_result=resolution or None,
                        )
                    )

                db.commit()

                flash("Протокол сохранён", "success")

                return redirect(
                    url_for("parent_meetings.index", group_id=selected_group_id)
                )

        meetings = []

        if selected_group_id:

            raw_meetings = (
                db.query(ParentMeeting).filter_by(group_id=int(selected_group_id)).all()
            )

            for m in raw_meetings:

                meetings.append(
                    {
                        "id": m.parent_meeting_id,
                        "date": (
                            m.meeting_date.strftime("%d.%m.%Y")
                            if m.meeting_date
                            else "—"
                        ),
                        "topic": m.topics or "—",
                    }
                )

            meetings.sort(key=lambda x: x["date"], reverse=True)

        edit_id = request.args.get("edit")

        edit_meeting = None

        if edit_id:

            edit_meeting = db.query(ParentMeeting).get(int(edit_id))

        return render_template(
            "parent_meetings.html",
            title="Родительские собрания",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            meetings=meetings,
            edit_meeting=edit_meeting,
            today=today,
        )

    finally:

        db.close()
