from .social_passport import generate_social_passport
from .dormitory_list import generate_dormitory_list
from .activists_group import generate_activists_group
from .extracurricular import generate_extracurricular
from .class_hours import generate_class_hours_attendance
from .observation_sheet import generate_observation_sheet
from .parent_meetings import generate_parent_meetings
from .individual_work import generate_individual_work
from .general_report import generate_general_report

__all__ = [
    "generate_social_passport",
    "generate_dormitory_list",
    "generate_activists_group",
    "generate_extracurricular",
    "generate_class_hours_attendance",
    "generate_observation_sheet",
    "generate_parent_meetings",
    "generate_individual_work",
    "generate_general_report",
]