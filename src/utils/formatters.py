from copyreg import clear_extension_cache


def format_group_name(group):

    spec = group.specialization.specialization_reduction

    course = group.course.course_name

    year_suffix = f"{group.creation_year % 100:02d}"
    try:
        qual = group.qualification.qualification_reduction
    except:
        qual = ""

    return f"{spec}-{course}{year_suffix}{qual}"
