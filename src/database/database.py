from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from werkzeug.security import generate_password_hash

from .models import Base, Curator, Person, Role
from config.config import DB_URL

engine = create_engine(DB_URL, pool_pre_ping=True, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
    """Создаёт все таблицы по моделям."""
    Base.metadata.create_all(bind=engine)


def create_default_admin(db: Session):
    """Создаёт базового администратора admin:admin, если его ещё нет."""
    if db.scalar(select(Curator).limit(1)) is not None:
        return  # БД уже инициализирована

    role = db.scalar(select(Role).where(Role.role_id == 1))
    if not role:
        role = Role(role_id=1, role_name="Администратор")
        db.add(role)

    person = Person(surname="Админ", name="Админ", patronymic="")
    db.add(person)
    db.flush()

    admin = Curator(
        person_id=person.person_id,
        login="admin",
        password_hash=generate_password_hash("admin", method="pbkdf2:sha256"),
        role_id=1,
    )
    db.add(admin)
    db.commit()


def init_db_with_admin():
    """Полная инициализация: таблицы + дефолтный админ."""
    init_db()
    db: Session = SessionLocal()
    try:
        create_default_admin(db)
    finally:
        db.close()