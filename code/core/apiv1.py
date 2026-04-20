# core/apiv1.py
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.security import HttpBearer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from courses.models import Course, CourseMember, Profile
from core.schemas import (
    RegisterIn, LoginIn, TokenOut, UserOut,
    CourseIn, CourseOut, DetailCourseOut, EnrollmentIn, EnrollmentOut
)
from typing import List
from django.db import IntegrityError
from functools import wraps


def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.auth
            if user.profile.role not in roles:
                raise HttpError(403, f"Role {user.profile.role} not allowed")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            return user
        except Exception:
            return None


apiv1 = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="API untuk Simple Learning Management System",
    auth=JWTAuth()
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@apiv1.post('auth/register', response={201: UserOut}, auth=None)
def register(request, data: RegisterIn):
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username already exists")
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email already exists")
    
    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name
    )
    profile = user.profile
    profile.role = data.role
    profile.save()
    return 201, user


@apiv1.post('auth/login', response=TokenOut, auth=None)
def login(request, data: LoginIn):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        raise HttpError(401, "Invalid credentials")
    tokens = get_tokens_for_user(user)
    return tokens


@apiv1.post('auth/refresh', response=TokenOut, auth=None)
def refresh_token(request, refresh: str):
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = RefreshToken(refresh)
        new_access = str(refresh_token.access_token)
        return {'access': new_access, 'refresh': refresh}
    except Exception:
        raise HttpError(401, "Invalid refresh token")


@apiv1.get('auth/me', response=UserOut)
def get_current_user(request):
    user = request.auth
    return user


@apiv1.put('auth/me', response=UserOut)
def update_profile(request, first_name: str = None, last_name: str = None, email: str = None):
    user = request.auth
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:
        user.email = email
    user.save()
    return user


@apiv1.get('hello/', auth=None)
def helloApi(request):
    return "Menyala abangkuh ..."


# ==================== Course Endpoints ====================

@apiv1.get('courses/', response=List[CourseOut], auth=None)
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


@apiv1.get('courses/{id}', response=DetailCourseOut, auth=None)
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
    """Membuat course baru (Instructor only)."""
    user = request.auth
    if user.profile.role != 'instructor':
        raise HttpError(403, "Only instructors can create courses")
    
    course = Course.objects.create(**data.dict(), teacher=user)
    return 201, course


@apiv1.patch('courses/{id}', response=CourseOut)
def updateCourse(request, id: int, data: CourseIn):
    """Mengupdate course (Owner or Admin)."""
    user = request.auth
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")
    
    if course.teacher != user and user.profile.role != 'admin':
        raise HttpError(403, "You can only update your own courses")
    
    for attr, value in data.dict().items():
        setattr(course, attr, value)
    course.save()
    return course


@apiv1.delete('courses/{id}', response={204: None})
def deleteCourse(request, id: int):
    """Menghapus course (Admin only)."""
    user = request.auth
    if user.profile.role != 'admin':
        raise HttpError(403, "Only admins can delete courses")
    
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")
    
    course.delete()
    return 204, None


# ==================== Enrollment Endpoints ====================

@apiv1.post('enrollments/', response={201: EnrollmentOut})
def enroll_course(request, data: EnrollmentIn):
    """Enroll to a course (Student only)."""
    user = request.auth
    if user.profile.role != 'student':
        raise HttpError(403, "Only students can enroll")
    
    try:
        course = Course.objects.get(pk=data.course_id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course not found")
    
    if CourseMember.objects.filter(course_id=course, user_id=user).exists():
        raise HttpError(400, "Already enrolled")
    
    member = CourseMember.objects.create(course_id=course, user_id=user)
    return 201, member


@apiv1.get('enrollments/my-courses', response=List[CourseOut])
def my_enrolled_courses(request):
    """Get my enrolled courses."""
    user = request.auth
    course_ids = CourseMember.objects.filter(user_id=user).values_list('course_id', flat=True)
    courses = Course.objects.filter(id__in=course_ids).select_related('teacher')
    return courses