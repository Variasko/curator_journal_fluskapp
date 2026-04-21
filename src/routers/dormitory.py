
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import (
    StudentInDormitory, Student, Person, 
    Group, StudentInGroup, Curator
)
from utils.formatters import format_group_name

dormitory_bp = Blueprint('dormitory', __name__, url_prefix='/dormitory')

@dormitory_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'person_id' not in session:
        return redirect(url_for('login'))
    
    curator_id = session['person_id']
    db: Session = SessionLocal()
    
    try:
        
        curator_groups = db.query(Group).filter_by(curator_id=curator_id).all()
        groups_data = [{'group_id': g.group_id, 'display_name': format_group_name(g)} for g in curator_groups]
        
        
        selected_group_id = request.args.get('group_id') or request.form.get('group_id')
        if not selected_group_id and groups_data:
            selected_group_id = groups_data[0]['group_id']
        
        
        if request.method == 'POST':
            action = request.form.get('action')
            student_id = request.form.get('student_id')
            room_number = request.form.get('room_number', '').strip()
            
            if action == 'delete' and student_id:
                db.query(StudentInDormitory).filter_by(
                    student_id=int(student_id)
                ).delete(synchronize_session=False)
                db.commit()
                flash('Запись удалена', 'success')
                return redirect(url_for('dormitory.index', group_id=selected_group_id))
            
            if action == 'save' and student_id and room_number:
                
                db.query(StudentInDormitory).filter_by(
                    student_id=int(student_id)
                ).delete(synchronize_session=False)
                
                
                db.add(StudentInDormitory(
                    student_id=int(student_id),
                    room_number=int(room_number)
                ))
                db.commit()
                flash('Данные сохранены', 'success')
                return redirect(url_for('dormitory.index', group_id=selected_group_id))

        
        dorm_list = []
        if selected_group_id:
            
            records = db.query(StudentInDormitory, Person)\
                .join(StudentInGroup, StudentInDormitory.student_id == StudentInGroup.student_id)\
                .join(Person, StudentInDormitory.student_id == Person.person_id)\
                .filter(StudentInGroup.group_id == int(selected_group_id))\
                .all()
            
            for rec, person in records:
                dorm_list.append({
                    'student_id': rec.student_id,
                    'full_name': f"{person.surname} {person.name} {person.patronymic or ''}".strip(),
                    'room': rec.room_number
                })
            
            dorm_list.sort(key=lambda x: (x['room'], x['full_name']))
        
        
        students_list = []
        if selected_group_id:
            results = db.query(StudentInGroup, Person)\
                .join(Person, StudentInGroup.student_id == Person.person_id)\
                .join(Student, StudentInGroup.student_id == Student.person_id)\
                .filter(StudentInGroup.group_id == int(selected_group_id))\
                .filter(Student.is_expelled == False)\
                .all()
            
            for sig, person in results:
                
                in_dorm = db.query(StudentInDormitory).filter_by(student_id=person.person_id).first()
                students_list.append({
                    'id': person.person_id,
                    'name': f"{person.surname} {person.name} {person.patronymic or ''}".strip(),
                    'in_dorm': bool(in_dorm)
                })
            students_list.sort(key=lambda x: x['name'])
        
        
        edit_student_id = request.args.get('edit')
        edit_student_name = None
        edit_room = None
        
        if edit_student_id:
            person = db.query(Person).filter_by(person_id=int(edit_student_id)).first()
            if person:
                edit_student_name = f"{person.surname} {person.name} {person.patronymic or ''}".strip()
            
            dorm_rec = db.query(StudentInDormitory).filter_by(student_id=int(edit_student_id)).first()
            if dorm_rec:
                edit_room = dorm_rec.room_number

        return render_template(
            'dormitory.html',
            title="Студенты в общежитии",
            groups=groups_data,
            current_group_id=int(selected_group_id) if selected_group_id else None,
            dorm_list=dorm_list,
            students_list=students_list,
            edit_student_id=edit_student_id,
            edit_student_name=edit_student_name,
            edit_room=edit_room
        )
        
    finally:
        db.close()