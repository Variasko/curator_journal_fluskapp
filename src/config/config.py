import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-prod")
DB_URL = os.getenv("DB_URL", "sqlite:///database.db")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
IS_FIRST_TIME = os.getenv("IS_FIRST_TIME", "False").lower()  in ("true", "1", "yes")

def is_debug() -> bool:
    """Возвращает, запущено ли приложение в режиме отладки."""
    return DEBUG

def is_first_run(db_path: str) -> bool:
    if IS_FIRST_TIME:
        return True

    if "sqlite:///" in db_path:
        path = db_path.replace("sqlite:///", "")
        return not os.path.exists(path)
    return False