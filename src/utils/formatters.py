def format_group_name(group):

    if not all([group.specialization, group.qualification, group.course]):

        return f"Группа #{group.group_id}"

    spec = group.specialization.specialization_reduction

    course = group.course.course_name

    year_suffix = f"{group.creation_year % 100:02d}"

    qual = group.qualification.qualification_reduction

    return f"{spec}-{course}{year_suffix}{qual}"
