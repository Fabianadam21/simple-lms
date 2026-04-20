# core/apiv1.py
from ninja import NinjaAPI
from ninja.errors import HttpError
from django.contrib.auth.models import User
from courses.models import Course
from core.schemas import CourseIn, CourseOut, DetailCourseOut
from typing import List


apiv1 = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="API untuk Simple Learning Management System"
)


@apiv1.get('hello/')
def helloApi(request):
    return "Menyala abangkuh ..."


# ==================== Course Endpoints ====================

@apiv1.get('courses/', response=List[CourseOut])
def listCourses(request, search: str = None, min_price: int = None, max_price: int = None):
    """Mengambil daftar semua course dengan filter opsional."""
    qs = Course.objects.select_related('teacher').all()
    if search:
        qs = qs.filter(name__icontains=search)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    return qs


@apiv1.get('courses/{id}', response=DetailCourseOut)
def detailCourse(request, id: int):
    """Mengambil detail course beserta daftar kontennya."""
    try:
        return Course.objects.prefetch_related(
            'coursecontent_set'
        ).select_related('teacher').get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")


@apiv1.post('courses/', response={201: CourseOut})
def createCourse(request, data: CourseIn):
    """Membuat course baru."""
    teacher = User.objects.first()
    if not teacher:
        raise HttpError(400, "Belum ada user teacher di database")

    course = Course.objects.create(**data.dict(), teacher=teacher)
    return 201, course


@apiv1.put('courses/{id}', response=CourseOut)
def updateCourse(request, id: int, data: CourseIn):
    """Mengupdate data course secara keseluruhan."""
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")

    for attr, value in data.dict().items():
        setattr(course, attr, value)
    course.save()

    return course


@apiv1.delete('courses/{id}', response={204: None})
def deleteCourse(request, id: int):
    """Menghapus course."""
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")

    course.delete()
    return 204, None