from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# =====================
# USER
# =====================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def get_role_display_custom(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


# =====================
# CATEGORY
# =====================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# =====================
# COURSE
# =====================
class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        """Optimized query untuk course listing view"""
        return self.select_related('instructor', 'category').prefetch_related('lessons')
    
    def filter_by_instructor(self, instructor):
        """Filter courses by instructor"""
        return self.filter(instructor=instructor)
    
    def active(self):
        """Filter only active courses"""
        return self.filter(is_active=True)


class Course(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        limit_choices_to={'role': 'instructor'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CourseQuerySet.as_manager()
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_lesson_count(self):
        """Get total lessons in course"""
        return self.lessons.count()


# =====================
# LESSON
# =====================
class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField()
    order = models.PositiveIntegerField(db_index=True)
    video_url = models.URLField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'order']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        unique_together = ('course', 'order')
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


# =====================
# ENROLLMENT
# =====================
class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self):
        """Optimized query untuk student dashboard"""
        return self.select_related('course__instructor', 'course__category').prefetch_related('progress__lesson')
    
    def active(self):
        """Get active enrollments only"""
        return self.filter(status='active')
    
    def for_course(self, course):
        """Get enrollments for specific course"""
        return self.filter(course=course)


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    objects = EnrollmentQuerySet.as_manager()
    
    class Meta:
        unique_together = ('student', 'course')
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"
    
    def get_progress_percentage(self):
        """Calculate course completion percentage"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed = self.progress.filter(is_completed=True).count()
        return int((completed / total_lessons) * 100)


# =====================
# PROGRESS
# =====================
class Progress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    is_completed = models.BooleanField(default=False, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('enrollment', 'lesson')
        verbose_name = 'Progress'
        verbose_name_plural = 'Progress'
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['enrollment', 'is_completed']),
            models.Index(fields=['lesson', 'is_completed']),
        ]
    
    def __str__(self):
        status = "✓ Completed" if self.is_completed else "○ In Progress"
        return f"{self.enrollment.student.username} - {self.lesson.title} [{status}]"