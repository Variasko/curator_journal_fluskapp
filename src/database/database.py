from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker


from .models import *

from config.config import DB_URL

engine = create_engine(DB_URL, pool_pre_ping=True)


SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def init_db():

    Base.metadata.create_all(bind=engine)
