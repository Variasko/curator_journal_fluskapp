import importlib
from flask import Blueprint

ROUTER_FILES = [
    "profile",
    "curators", 
    "students",
    "groups",
    "specializations",
    "qualifications",
    "roles",
    "parents",
    "student_parents",
    "social_statuses",
    "posts",
    "hobbies",
    "import_data",
    "social_passport",
    "activists",
    "dormitory",
    "extracurricular",
    "observation_list",
    "parent_meetings",
    "individual_work",
    "class_hours",
    "reports",
]

_blueprints = []

for filename in ROUTER_FILES:
    try:
        module = importlib.import_module(f".{filename}", package="routers")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, Blueprint):
                _blueprints.append(attr)
                break
        else:
            print(f"⚠️ В модуле '{filename}.py' не найдена переменная типа Blueprint")
            
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать router '{filename}': {e}")

__all__ = ["get_blueprints"] + ROUTER_FILES


def get_blueprints():
    """Возвращает копию списка всех найденных Blueprint."""
    return _blueprints.copy()