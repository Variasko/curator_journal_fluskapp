from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import SocialStatus

statuses_bp = Blueprint('social_statuses', __name__, url_prefix='/admin/social-statuses')

@statuses_bp.route('/', methods=['GET', 'POST'])
def manage_social_statuses():
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'delete':
                item = db.query(SocialStatus).get(int(request.form.get('item_id')))
                if item: db.delete(item); db.commit()
                flash('Удалено', 'success')
                return redirect(url_for('social_statuses.manage_social_statuses'))

            if action in ('add', 'edit'):
                name = request.form.get('name', '').strip()
                if not name:
                    flash('Название обязательно', 'error')
                    return redirect(url_for('social_statuses.manage_social_statuses'))

                if action == 'edit':
                    item = db.query(SocialStatus).get(int(request.form.get('item_id')))
                    if item: item.status_name = name
                else:
                    db.add(SocialStatus(status_name=name))
                db.commit()
                flash('Сохранено', 'success')
                return redirect(url_for('social_statuses.manage_social_statuses'))

        items = db.query(SocialStatus).all()
        edit_item = None
        if request.args.get('edit'): edit_item = db.query(SocialStatus).get(int(request.args.get('edit')))
        return render_template('admin_social_statuses.html', title="Социальные статусы", items=items, edit_item=edit_item)
    finally:
        db.close()