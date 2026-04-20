# core/schemas.py
from ninja import Schema, Field
from datetime import datetime
from typing import Optional, List


class UserOut(Schema):
    """Schema untuk data User yang dikembalikan dalam response."""
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    role: str = Field(..., alias="profile.role")


class RegisterIn(Schema):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = 'student'


class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    access: str
    refresh: str


class CourseIn(Schema):
    """Schema untuk input saat membuat/mengupdate Course."""
    name: str
    description: str = '-'
    price: int = 10000


class CourseOut(Schema):
    """Schema untuk output data Course."""
    id: int
    name: str
    description: str
    price: int
    image: Optional[str] = ''
    teacher: UserOut
    created_at: datetime
    updated_at: datetime


class ContentTitleOut(Schema):
    """Schema untuk menampilkan judul konten saja."""
    id: int
    name: str


class DetailCourseOut(CourseOut):
    """Schema untuk detail Course beserta daftar konten."""
    contents: List[ContentTitleOut] = Field(
        ..., alias="coursecontent_set"
    )


class EnrollmentIn(Schema):
    course_id: int


class ProgressIn(Schema):
    content_id: int
    completed: bool = True


class ProgressOut(Schema):
    id: int
    content_id: int
    member_id: int
    completed: bool
    completed_at: datetime