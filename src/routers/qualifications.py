from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Qualification

quals_bp = Blueprint('qualifications', __name__, url_prefix='/admin/qualifications')

@quals_bp.route('/', methods=['GET', 'POST'])
def manage_qualifications():
    if 'person_id' not in session:
        return redirect(url_for('login'))
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'delete':
                qual_id = int(request.form.get('qual_id'))
                qual = db.query(Qualification).filter(Qualification.qualification_id == qual_id).first()
                if qual:
                    db.delete(qual)
                    db.commit()
                    flash('Квалификация удалена', 'success')
                return redirect(url_for('qualifications.manage_qualifications'))

            if action in ('add', 'edit'):
                name = request.form.get('name', '').strip()
                reduction = request.form.get('reduction', '').strip()

                if not name or not reduction:
                    flash('Заполните все обязательные поля', 'error')
                    return redirect(url_for('qualifications.manage_qualifications'))

                if action == 'edit':
                    qual_id = int(request.form.get('qual_id'))
                    qual = db.query(Qualification).filter(Qualification.qualification_id == qual_id).first()
                    if qual:
                        qual.qualification_name = name
                        qual.qualification_reduction = reduction
                else:
                    new_qual = Qualification(qualification_name=name, qualification_reduction=reduction)
                    db.add(new_qual)

                db.commit()
                flash('Данные сохранены', 'success')
                return redirect(url_for('qualifications.manage_qualifications'))

        items = db.query(Qualification).all()
        edit_item = None
        edit_id = request.args.get('edit')
        if edit_id:
            edit_item = db.query(Qualification).filter(Qualification.qualification_id == int(edit_id)).first()

        return render_template('admin_qualifications.html', title="Квалификации", items=items, edit_item=edit_item)
    finally:
        db.close()