"""
Скрипт начального заполнения справочных таблиц БД.
Запуск: python -m utils.seed или python utils/seed.py
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.database import SessionLocal, engine, Base
from database.models import Role, Specialization, Qualification

ROLES_DATA = [
    {"role_id": 1, "role_name": "Администратор", "role_description": "Полный доступ ко всем функциям системы"},
    {"role_id": 2, "role_name": "Куратор", "role_description": "Управление группой, отчётность, работа со студентами"},
    {"role_id": 3, "role_name": "Супервайзер", "role_description": "Просмотр отчётов и аналитика по нескольким группам"},
]

def _upsert_model(session: Session, model, data_list: list[dict], key_fields: list[str]):
    """
    Универсальная функция upsert: добавляет запись, если нет, или обновляет существующую.
    :param model: SQLAlchemy-модель (Role, Specialization, etc.)
    :param data_list: список словарей с данными
    :param key_fields: поля, по которым проверяется уникальность (обычно ['id'])
    """
    for data in data_list:
        filters = {field: data[field] for field in key_fields if field in data}
        existing = session.scalar(select(model).filter_by(**filters))
        
        if existing:
            for k, v in data.items():
                if k not in key_fields:
                    setattr(existing, k, v)
            print(f"↻ Обновлено: {model.__tablename__} #{data.get(key_fields[0])}")
        else:
            instance = model(**data)
            session.add(instance)
            print(f"✓ Добавлено: {model.__tablename__} #{data.get(key_fields[0])} — {data.get('name') or data.get('role_name') or data.get('specialization_name') or data.get('qualification_name')}")


def seed_roles(session: Session):
    _upsert_model(session, Role, ROLES_DATA, key_fields=["role_id"])

def run_seed():
    """Запускает заполнение всех справочников."""
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("🌱 Запуск заполнения справочных таблиц...")
        
        seed_roles(db)
        
        db.commit()
        print("✅ Готово! Данные сохранены в БД.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при заполнении: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()