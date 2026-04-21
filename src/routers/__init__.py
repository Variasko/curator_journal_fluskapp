from .profile import profile_bp

from .curators import curators_bp

from .students import students_bp

from .groups import groups_bp

from .specializations import specs_bp

from .qualifications import quals_bp

from .roles import roles_bp

from .parents import parents_bp

from .student_parents import student_parents_bp

from .social_statuses import statuses_bp

from .posts import posts_bp

from .hobbies import hobbies_bp

from .import_data import import_bp

from .social_passport import social_bp

from .activists import activists_bp

from .dormitory import dormitory_bp

from .extracurricular import extracurricular_bp

from .observation_list import observation_bp

from .parent_meetings import parent_meetings_bp

from .individual_work import indiv_bp

from .class_hours import class_hours_bp

__all__ = [
    "profile_bp",
    "curators_bp",
    "students_bp",
    "groups_bp",
    "specs_bp",
    "quals_bp",
    "roles_bp",
    "parents_bp",
    "student_parents_bp",
    "statuses_bp",
    "posts_bp",
    "hobbies_bp",
    "import_bp",
    "social_bp",
    "activists_bp",
    "dormitory_bp",
    "extracurricular_bp",
    "observation_bp",
    "parent_meetings_bp",
    "indiv_bp",
    "class_hours_bp",
]
