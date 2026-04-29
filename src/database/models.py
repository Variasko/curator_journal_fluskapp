from datetime import date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase): ...


class Course(Base):

    __tablename__ = "course"

    course_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    course_name: Mapped[str] = mapped_column(String(1))


class Role(Base):

    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    role_name: Mapped[str] = mapped_column(String(50))

    role_description: Mapped[str | None] = mapped_column(Text, nullable=True)


class SocialStatus(Base):

    __tablename__ = "social_status"

    status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    status_name: Mapped[str] = mapped_column(String(50))


class Specialization(Base):

    __tablename__ = "specialization"

    specialization_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    specialization_name: Mapped[str] = mapped_column(String(50))

    specialization_reduction: Mapped[str] = mapped_column(String(5))


class Qualification(Base):

    __tablename__ = "qualification"

    qualification_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    qualification_name: Mapped[str] = mapped_column(String(50))

    qualification_reduction: Mapped[str] = mapped_column(String(5))


class HobbyType(Base):

    __tablename__ = "hobby_type"

    hobby_type_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    hobby_type_name: Mapped[str] = mapped_column(String(50))


class PostInGroupType(Base):

    __tablename__ = "post_in_group_type"

    post_in_group_type_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    post_in_group_type_name: Mapped[str] = mapped_column(String(50))


class Person(Base):

    __tablename__ = "person"

    person_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    surname: Mapped[str] = mapped_column(String(50))

    name: Mapped[str] = mapped_column(String(50))

    patronymic: Mapped[str | None] = mapped_column(String(50), nullable=True)

    photo: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    passport_number: Mapped[str | None] = mapped_column(String(6), nullable=True)

    passport_serial: Mapped[str | None] = mapped_column(String(4), nullable=True)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Curator(Base):

    __tablename__ = "curator"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    login: Mapped[str] = mapped_column(String(30))

    password_hash: Mapped[str] = mapped_column(Text)

    role_id: Mapped[int] = mapped_column(ForeignKey("role.role_id"))

    person: Mapped["Person"] = relationship("Person")

    role: Mapped["Role"] = relationship("Role")


class Student(Base):

    __tablename__ = "student"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    is_expelled: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0"
    )

    person: Mapped["Person"] = relationship("Person")


class Group(Base):

    __tablename__ = "group"

    group_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    specialization_id: Mapped[int] = mapped_column(
        ForeignKey(
            "specialization.specialization_id", onupdate="CASCADE", ondelete="CASCADE"
        )
    )

    qualification_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "qualification.qualification_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=True,
    )

    course_id: Mapped[int] = mapped_column(ForeignKey("course.course_id"))

    creation_year: Mapped[int] = mapped_column(Integer)

    curator_id: Mapped[int] = mapped_column(
        ForeignKey("curator.person_id", onupdate="CASCADE", ondelete="CASCADE")
    )

    specialization: Mapped["Specialization"] = relationship("Specialization")

    qualification: Mapped["Qualification"] = relationship("Qualification")

    course: Mapped["Course"] = relationship("Course")

    curator: Mapped["Curator"] = relationship("Curator")


class ClassHour(Base):

    __tablename__ = "class_hour"

    class_hour_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    class_hour_date: Mapped[date] = mapped_column(Date)

    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.group_id", onupdate="CASCADE", ondelete="CASCADE")
    )

    group: Mapped["Group"] = relationship("Group")


class Parent(Base):

    __tablename__ = "parent"

    parent_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    surname: Mapped[str] = mapped_column(String(50))

    name: Mapped[str] = mapped_column(String(50))

    patronymic: Mapped[str | None] = mapped_column(String(50), nullable=True)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)


class ParentIndividualWork(Base):

    __tablename__ = "parent_individual_work"

    parent_individual_work_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    parent_id: Mapped[int] = mapped_column(ForeignKey("parent.parent_id"))

    date: Mapped[date] = mapped_column(Date)

    topic: Mapped[str] = mapped_column(Text)

    result: Mapped[str] = mapped_column(Text)

    parent: Mapped["Parent"] = relationship("Parent")


class ParentMeeting(Base):

    __tablename__ = "parent_meeting"

    parent_meeting_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.group_id", onupdate="CASCADE", ondelete="CASCADE")
    )

    curator_id: Mapped[int] = mapped_column(ForeignKey("curator.person_id"))

    meeting_date: Mapped[date] = mapped_column(Date)

    invited: Mapped[str | None] = mapped_column(Text, nullable=True)

    visited_count: Mapped[int] = mapped_column(Integer, default=0)

    unvisited: Mapped[int] = mapped_column(Integer, default=0)

    excused_count: Mapped[int] = mapped_column(Integer, default=0)

    topics: Mapped[str | None] = mapped_column(Text, nullable=True)

    speakers: Mapped[str | None] = mapped_column(Text, nullable=True)

    meeting_result: Mapped[str | None] = mapped_column(Text, nullable=True)

    group: Mapped["Group"] = relationship("Group")

    curator: Mapped["Curator"] = relationship("Curator")


class ObservationList(Base):

    __tablename__ = "observation_list"

    observation_list_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    student_id: Mapped[int] = mapped_column(ForeignKey("student.person_id"))

    observation_date: Mapped[date] = mapped_column(Date)

    characteristic: Mapped[str] = mapped_column(Text)

    student: Mapped["Student"] = relationship("Student")


class StudentIndividualWork(Base):

    __tablename__ = "student_individual_work"

    student_individual_work_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    student_id: Mapped[int] = mapped_column(ForeignKey("student.person_id"))

    date: Mapped[date] = mapped_column(Date)

    topic: Mapped[str] = mapped_column(Text)

    result: Mapped[str] = mapped_column(Text)

    student: Mapped["Student"] = relationship("Student")


class PostInGroup(Base):

    __tablename__ = "post_in_group"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    post_in_group_type_id: Mapped[int] = mapped_column(
        ForeignKey(
            "post_in_group_type.post_in_group_type_id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.course_id"), primary_key=True
    )

    student: Mapped["Student"] = relationship("Student")

    post_in_group_type: Mapped["PostInGroupType"] = relationship("PostInGroupType")

    course: Mapped["Course"] = relationship("Course")


class SocialPassport(Base):

    __tablename__ = "social_passport"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    social_status_id: Mapped[int] = mapped_column(
        ForeignKey("social_status.status_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    student: Mapped["Student"] = relationship("Student")

    social_status: Mapped["SocialStatus"] = relationship("SocialStatus")


class StudentHobby(Base):

    __tablename__ = "student_hobby"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    hobby_type_id: Mapped[int] = mapped_column(
        ForeignKey("hobby_type.hobby_type_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    student: Mapped["Student"] = relationship("Student")

    hobby_type: Mapped["HobbyType"] = relationship("HobbyType")


class StudentInDormitory(Base):

    __tablename__ = "student_in_dormitory"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id"), primary_key=True
    )

    room_number: Mapped[int] = mapped_column(primary_key=True)

    student: Mapped["Student"] = relationship("Student")


class StudentInGroup(Base):

    __tablename__ = "student_in_group"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id"), primary_key=True
    )

    group_id: Mapped[int] = mapped_column(
        ForeignKey("group.group_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    creation_date: Mapped[date] = mapped_column(Date)

    student: Mapped["Student"] = relationship("Student")

    group: Mapped["Group"] = relationship("Group")


class StudentParent(Base):

    __tablename__ = "student_parent"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    parent_id: Mapped[int] = mapped_column(
        ForeignKey("parent.parent_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    student: Mapped["Student"] = relationship("Student")

    parent: Mapped["Parent"] = relationship("Parent")


class VisitingClassHour(Base):

    __tablename__ = "visiting_class_hour"

    class_hour_id: Mapped[int] = mapped_column(
        ForeignKey("class_hour.class_hour_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("student.person_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    is_visited: Mapped[bool] = mapped_column(Boolean)

    class_hour: Mapped["ClassHour"] = relationship("ClassHour")

    student: Mapped["Student"] = relationship("Student")
