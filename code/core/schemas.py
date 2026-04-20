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