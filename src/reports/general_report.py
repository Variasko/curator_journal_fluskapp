import io
from sqlalchemy.orm import Session
from openpyxl import Workbook
from . import (
    generate_social_passport, generate_dormitory_list, generate_activists_group,
    generate_extracurricular, generate_class_hours_attendance, generate_observation_sheet,
    generate_parent_meetings, generate_individual_work
)
from database.models import Group
from utils.formatters import format_group_name
from .helpers import copy_worksheet_to_master

def generate_general_report(group_id: int, db: Session) -> tuple[io.BytesIO, str] | None:
    group = db.query(Group).filter_by(group_id=group_id).first()
    if not group:
        return None

    group_name = format_group_name(group)
    master_wb = Workbook()

    generators = [
        generate_social_passport, generate_dormitory_list, generate_activists_group,
        generate_extracurricular, generate_class_hours_attendance, generate_observation_sheet,
        generate_individual_work, generate_parent_meetings
    ]

    for gen_func in generators:
        result = gen_func(group_id, db)
        if result:
            copy_worksheet_to_master(result[0], master_wb)

    if "Sheet" in master_wb.sheetnames:
        del master_wb["Sheet"]

    output = io.BytesIO()
    master_wb.save(output)
    output.seek(0)
    return output, group_name