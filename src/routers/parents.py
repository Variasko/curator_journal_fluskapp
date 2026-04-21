from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Parent

parents_bp = Blueprint('parents', __name__, url_prefix='/admin/parents')

@parents_bp.route('/', methods=['GET', 'POST'])
def manage_parents():
    if 'person_id' not in session:
        return redirect(url_for('login'))
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'delete':
                parent = db.query(Parent).get(int(request.form.get('parent_id')))
                if parent: db.delete(parent); db.commit()
                flash('Родитель удалён', 'success')
                return redirect(url_for('parents.manage_parents'))

            if action in ('add', 'edit'):
                surname = request.form.get('surname', '').strip()
                name = request.form.get('name', '').strip()
                patronymic = request.form.get('patronymic', '').strip()
                phone = request.form.get('phone', '').strip()
                if not surname or not name:
                    flash('ФИО обязательно', 'error')
                    return redirect(url_for('parents.manage_parents'))

                if action == 'edit':
                    parent = db.query(Parent).get(int(request.form.get('parent_id')))
                    if parent: parent.surname, parent.name, parent.patronymic, parent.phone = surname, name, patronymic or None, phone or None
                else:
                    db.add(Parent(surname=surname, name=name, patronymic=patronymic or None, phone=phone or None))
                db.commit()
                flash('Сохранено', 'success')
                return redirect(url_for('parents.manage_parents'))

        items = db.query(Parent).all()
        edit_item = None
        if request.args.get('edit'): edit_item = db.query(Parent).get(int(request.args.get('edit')))
        return render_template('admin_parents.html', title="Родители", items=items, edit_item=edit_item)
    finally:
        db.close()