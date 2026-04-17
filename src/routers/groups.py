from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Group, Specialization, Qualification, Course, Curator

groups_bp = Blueprint('groups', __name__, url_prefix='/admin/groups')

def format_group_name(group):
    """Формирует название по шаблону: {Спец}-{Курс}{Год}{Квал}"""
    if not all([group.specialization, group.qualification, group.course]):
        return f"Группа #{group.group_id}"
    
    spec = group.specialization.specialization_reduction
    course = group.course.course_name
    year_suffix = f"{group.creation_year % 100:02d}"  # Берём последние 2 цифры (2024 -> 24)
    qual = group.qualification.qualification_reduction
    
    return f"{spec}-{course}{year_suffix}{qual}"

@groups_bp.route('/', methods=['GET', 'POST'])
def manage_groups():
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'delete':
                group_id = int(request.form.get('group_id'))
                group = db.query(Group).get(group_id)
                if group:
                    db.delete(group)
                    db.commit()
                    flash('Группа удалена', 'success')
                return redirect(url_for('groups.manage_groups'))

            if action in ('add', 'edit'):
                spec_id = request.form.get('specialization_id')
                qual_id = request.form.get('qualification_id')
                course_id = request.form.get('course_id')
                creation_year = request.form.get('creation_year')
                curator_id = request.form.get('curator_id')

                if not all([spec_id, qual_id, course_id, creation_year]):
                    flash('Заполните обязательные поля', 'error')
                    return redirect(url_for('groups.manage_groups'))

                curator_id = int(curator_id) if curator_id else None

                if action == 'edit':
                    group_id = int(request.form.get('group_id'))
                    group = db.query(Group).get(group_id)
                    if group:
                        group.specialization_id = int(spec_id)
                        group.qualification_id = int(qual_id)
                        group.course_id = int(course_id)
                        group.creation_year = int(creation_year)
                        group.curator_id = curator_id
                else:
                    new_group = Group(
                        specialization_id=int(spec_id),
                        qualification_id=int(qual_id),
                        course_id=int(course_id),
                        creation_year=int(creation_year),
                        curator_id=curator_id
                    )
                    db.add(new_group)

                db.commit()
                flash('Группа сохранена', 'success')
                return redirect(url_for('groups.manage_groups'))

        # GET: Сбор данных
        groups_raw = db.query(Group).all()
        # Сразу формируем список с готовыми названиями для шаблона
        groups_data = [{'group': g, 'display_name': format_group_name(g)} for g in groups_raw]

        specs = db.query(Specialization).all()
        quals = db.query(Qualification).all()
        courses = db.query(Course).all()
        curators = db.query(Curator).all()

        edit_group = None
        edit_id = request.args.get('edit')
        if edit_id:
            edit_group = db.query(Group).get(int(edit_id))

        return render_template('admin_groups.html',
                               title="Группы",
                               groups_data=groups_data,
                               specs=specs, quals=quals, courses=courses, curators=curators,
                               edit_group=edit_group)
    finally:
        db.close()