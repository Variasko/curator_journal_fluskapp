from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Specialization

specs_bp = Blueprint('specializations', __name__, url_prefix='/admin/specializations')

@specs_bp.route('/', methods=['GET', 'POST'])
def manage_specializations():
    if 'person_id' not in session:
        return redirect(url_for('login'))
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'delete':
                spec_id = int(request.form.get('spec_id'))
                spec = db.query(Specialization).filter(Specialization.specialization_id == spec_id).first()
                if spec:
                    db.delete(spec)
                    db.commit()
                    flash('Специальность удалена', 'success')
                return redirect(url_for('specializations.manage_specializations'))

            if action in ('add', 'edit'):
                name = request.form.get('name', '').strip()
                reduction = request.form.get('reduction', '').strip()

                if not name or not reduction:
                    flash('Заполните все обязательные поля', 'error')
                    return redirect(url_for('specializations.manage_specializations'))

                if action == 'edit':
                    spec_id = int(request.form.get('spec_id'))
                    spec = db.query(Specialization).filter(Specialization.specialization_id == spec_id).first()
                    if spec:
                        spec.specialization_name = name
                        spec.specialization_reduction = reduction
                else:
                    new_spec = Specialization(specialization_name=name, specialization_reduction=reduction)
                    db.add(new_spec)

                db.commit()
                flash('Данные сохранены', 'success')
                return redirect(url_for('specializations.manage_specializations'))

        items = db.query(Specialization).all()
        edit_item = None
        edit_id = request.args.get('edit')
        if edit_id:
            edit_item = db.query(Specialization).filter(Specialization.specialization_id == int(edit_id)).first()

        return render_template('admin_specializations.html', title="Специальности", items=items, edit_item=edit_item)
    finally:
        db.close()