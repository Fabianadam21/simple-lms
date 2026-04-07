from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import User, Category, Course, Lesson, Enrollment, Progress


# =====================
# USER ADMIN
# =====================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_full_name', 'role_badge', 'email', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def role_badge(self, obj):
        """Display role as colored badge"""
        colors = {
            'admin': '#ff5722',
            'instructor': '#2196f3',
            'student': '#4caf50'
        }
        color = colors.get(obj.role, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'


# =====================
# CATEGORY ADMIN
# =====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'get_courses_count', 'get_subcategories_count', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Hierarchy', {'fields': ('parent',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_courses_count(self, obj):
        """Count courses in this category"""
        return obj.courses.count()
    get_courses_count.short_description = 'Courses'
    
    def get_subcategories_count(self, obj):
        """Count subcategories"""
        return obj.children.count()
    get_subcategories_count.short_description = 'Subcategories'


# =====================
# LESSON INLINE
# =====================
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'duration_minutes', 'video_url', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('order',)


# =====================
# COURSE ADMIN
# =====================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor_link', 'category', 'get_lesson_count', 'get_student_count', 'is_active_badge', 'created_at')
    list_filter = ('is_active', 'category', 'instructor', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'get_enrollments_count')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description')}),
        ('Organization', {'fields': ('instructor', 'category')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
        ('Statistics', {'fields': ('get_enrollments_count',)}),
    )
    inlines = [LessonInline]
    
    def instructor_link(self, obj):
        """Link to instructor"""
        return obj.instructor.get_full_name() or obj.instructor.username
    instructor_link.short_description = 'Instructor'
    
    def get_lesson_count(self, obj):
        """Count lessons in course"""
        return obj.lessons.count()
    get_lesson_count.short_description = 'Lessons'
    
    def get_student_count(self, obj):
        """Count enrolled students"""
        return obj.enrollments.filter(status='active').count()
    get_student_count.short_description = 'Students'
    
    def is_active_badge(self, obj):
        """Display active status as badge"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    def get_enrollments_count(self, obj):
        """Get total enrollments"""
        if obj.pk:
            return obj.enrollments.count()
        return 0
    get_enrollments_count.short_description = 'Total Enrollments'


# =====================
# LESSON ADMIN
# =====================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes', 'has_video', 'get_progress_count', 'created_at')
    list_filter = ('course', 'created_at', 'duration_minutes')
    search_fields = ('title', 'description', 'content', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('course', 'title', 'description', 'content')}),
        ('Media', {'fields': ('video_url', 'duration_minutes')}),
        ('Organization', {'fields': ('order',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def has_video(self, obj):
        """Check if lesson has video"""
        if obj.video_url:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: gray;">—</span>')
    has_video.short_description = 'Video'
    
    def get_progress_count(self, obj):
        """Count completed progress"""
        completed = obj.progress.filter(is_completed=True).count()
        total = obj.progress.count()
        return f"{completed}/{total}"
    get_progress_count.short_description = 'Progress'


# =====================
# PROGRESS INLINE
# =====================
class ProgressInline(admin.TabularInline):
    model = Progress
    extra = 0
    fields = ('lesson', 'is_completed', 'started_at', 'completed_at')
    readonly_fields = ('started_at', 'completed_at')
    can_delete = False


# =====================
# ENROLLMENT ADMIN
# =====================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'course', 'status_badge', 'get_progress_percentage', 'enrolled_at', 'completed_at')
    list_filter = ('status', 'enrolled_at', 'course', 'course__category')
    search_fields = ('student__username', 'student__email', 'course__title')
    readonly_fields = ('enrolled_at', 'get_progress_percentage_html')
    fieldsets = (
        (None, {'fields': ('student', 'course')}),
        ('Status', {'fields': ('status', 'enrolled_at', 'completed_at')}),
        ('Progress', {'fields': ('get_progress_percentage_html',)}),
    )
    inlines = [ProgressInline]
    
    def student_name(self, obj):
        """Display full student name"""
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student__username'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'active': '#4caf50',
            'completed': '#2196f3',
            'dropped': '#f44336'
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_progress_percentage_html(self, obj):
        """Display progress as styled bar"""
        percentage = obj.get_progress_percentage()
        return format_html(
            '<div style="width: 200px; background-color: #e0e0e0; border-radius: 3px; height: 20px;">'
            '<div style="width: {}%; background-color: #4caf50; height: 100%; border-radius: 3px; text-align: center; color: white; font-weight: bold;">{}</div>'
            '</div>',
            percentage,
            f'{percentage}%'
        )
    get_progress_percentage_html.short_description = 'Progress'


# =====================
# PROGRESS ADMIN
# =====================
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'student_name', 'is_completed_badge', 'started_at', 'completed_at')
    list_filter = ('is_completed', 'started_at', 'completed_at', 'lesson__course')
    search_fields = ('enrollment__student__username', 'lesson__title')
    readonly_fields = ('started_at', 'completed_at')
    fieldsets = (
        (None, {'fields': ('enrollment', 'lesson')}),
        ('Status', {'fields': ('is_completed', 'completed_at')}),
        ('Timestamps', {'fields': ('started_at',)}),
    )
    
    def student_name(self, obj):
        """Display student name from enrollment"""
        return obj.enrollment.student.get_full_name() or obj.enrollment.student.username
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'enrollment__student__username'
    
    def is_completed_badge(self, obj):
        """Display completion status as badge"""
        if obj.is_completed:
            return format_html('<span style="color: green; font-weight: bold;">✓ Completed</span>')
        return format_html('<span style="color: orange; font-weight: bold;">○ In Progress</span>')
    is_completed_badge.short_description = 'Completion Status'

