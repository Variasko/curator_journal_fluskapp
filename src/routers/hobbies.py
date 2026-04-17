from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import HobbyType

hobbies_bp = Blueprint('hobbies', __name__, url_prefix='/admin/hobbies')

@hobbies_bp.route('/', methods=['GET', 'POST'])
def manage_hobbies():
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'delete':
                hobby_id = int(request.form.get('item_id'))
                hobby = db.query(HobbyType).get(hobby_id)
                if hobby:
                    db.delete(hobby)
                    db.commit()
                    flash('Тип хобби удалён', 'success')
                return redirect(url_for('hobbies.manage_hobbies'))

            if action in ('add', 'edit'):
                name = request.form.get('name', '').strip()
                if not name:
                    flash('Название обязательно', 'error')
                    return redirect(url_for('hobbies.manage_hobbies'))

                if action == 'edit':
                    hobby_id = int(request.form.get('item_id'))
                    hobby = db.query(HobbyType).get(hobby_id)
                    if hobby:
                        hobby.hobby_type_name = name
                else:
                    db.add(HobbyType(hobby_type_name=name))
                
                db.commit()
                flash('Сохранено', 'success')
                return redirect(url_for('hobbies.manage_hobbies'))

        items = db.query(HobbyType).all()
        edit_item = None
        edit_id = request.args.get('edit')
        if edit_id:
            edit_item = db.query(HobbyType).get(int(edit_id))

        return render_template('admin_hobbies.html', title="Виды хобби", items=items, edit_item=edit_item)
    finally:
        db.close()