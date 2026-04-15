from functools import wraps
from flask import redirect, url_for, session, flash, request
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Генерирует криптографический хеш пароля (pbkdf2:sha256)"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля сохранённому хешу"""
    return check_password_hash(hashed_password, password)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "person_id" not in session:
            flash("Для доступа к странице необходимо авторизоваться", "warning")
            # Сохраняем URL, чтобы вернуть пользователя после входа
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function