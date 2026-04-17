from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import PostInGroupType

posts_bp = Blueprint('posts', __name__, url_prefix='/admin/posts')

@posts_bp.route('/', methods=['GET', 'POST'])
def manage_posts():
    db: Session = SessionLocal()
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'delete':
                post_id = int(request.form.get('item_id'))
                post = db.query(PostInGroupType).get(post_id)
                if post:
                    db.delete(post)
                    db.commit()
                    flash('Должность удалена', 'success')
                return redirect(url_for('posts.manage_posts'))

            if action in ('add', 'edit'):
                name = request.form.get('name', '').strip()
                if not name:
                    flash('Название обязательно', 'error')
                    return redirect(url_for('posts.manage_posts'))

                if action == 'edit':
                    post_id = int(request.form.get('item_id'))
                    post = db.query(PostInGroupType).get(post_id)
                    if post:
                        post.post_in_group_type_name = name
                else:
                    db.add(PostInGroupType(post_in_group_type_name=name))
                
                db.commit()
                flash('Сохранено', 'success')
                return redirect(url_for('posts.manage_posts'))

        items = db.query(PostInGroupType).all()
        edit_item = None
        edit_id = request.args.get('edit')
        if edit_id:
            edit_item = db.query(PostInGroupType).get(int(edit_id))

        return render_template('admin_posts.html', title="Должности в группе", items=items, edit_item=edit_item)
    finally:
        db.close()