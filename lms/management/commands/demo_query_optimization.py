"""
Management command untuk demo query optimization
Menunjukkan N+1 problem dan solusinya dengan select_related dan prefetch_related
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import CaptureQueriesContext
from lms.models import Course, Enrollment


class Command(BaseCommand):
    help = 'Demo query optimization - N+1 problem dan solution'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('DJANGO ORM QUERY OPTIMIZATION DEMO'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        # Demo 1: N+1 Problem - Course Listing
        self.demo_n_plus_one_course()

        # Demo 2: Optimized - Course Listing with select_related
        self.demo_optimized_course_with_select_related()

        # Demo 3: N+1 Problem - Enrollment Dashboard
        self.demo_n_plus_one_enrollment()

        # Demo 4: Optimized - Enrollment Dashboard
        self.demo_optimized_enrollment()

    def demo_n_plus_one_course(self):
        """Demo N+1 problem saat listing courses"""
        self.stdout.write('\n' + self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('DEMO 1: N+1 PROBLEM - Course Listing (Naive)'))
        self.stdout.write(self.style.WARNING('=' * 80))

        with CaptureQueriesContext(connection) as context:
            courses = Course.objects.all()  # Query 1
            for course in courses:
                # Setiap iterasi membuat query baru untuk instructor dan category
                instructor_name = course.instructor.username
                category_name = course.category.name if course.category else 'None'

        self.stdout.write(f'Total Queries: {len(context)} ❌\n')
        for i, query in enumerate(context, 1):
            self.stdout.write(f'{i}. {query["sql"][:100]}...')
        
        self.print_analysis(
            query_count=len(context),
            is_optimized=False,
            explanation='❌ N+1 Problem: 1 query untuk courses + N queries untuk setiap instructor & category'
        )

    def demo_optimized_course_with_select_related(self):
        """Demo optimized course listing dengan select_related"""
        self.stdout.write('\n' + self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('DEMO 2: OPTIMIZED - Course Listing with select_related'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        with CaptureQueriesContext(connection) as context:
            # Gunakan for_listing() custom manager
            courses = Course.objects.for_listing()
            for course in courses:
                instructor_name = course.instructor.username
                category_name = course.category.name if course.category else 'None'

        self.stdout.write(f'Total Queries: {len(context)} ✓\n')
        for i, query in enumerate(context, 1):
            self.stdout.write(f'{i}. {query["sql"][:100]}...')
        
        self.print_analysis(
            query_count=len(context),
            is_optimized=True,
            explanation='✓ Optimized: select_related() menggabungkan instructor & category dalam 1 query. prefetch_related() untuk lessons.'
        )

    def demo_n_plus_one_enrollment(self):
        """Demo N+1 problem saat listing enrollments"""
        self.stdout.write('\n' + self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('DEMO 3: N+1 PROBLEM - Student Dashboard (Naive)'))
        self.stdout.write(self.style.WARNING('=' * 80))

        with CaptureQueriesContext(connection) as context:
            enrollments = Enrollment.objects.all()
            for enrollment in enrollments:
                # Multiple queries untuk setiap akses
                course_title = enrollment.course.title
                instructor = enrollment.course.instructor.username
                progress_items = list(enrollment.progress.all())
                progress_count = len(progress_items)

        self.stdout.write(f'Total Queries: {len(context)} ❌\n')
        for i, query in enumerate(context[:10], 1):  # Show first 10
            self.stdout.write(f'{i}. {query["sql"][:100]}...')
        if len(context) > 10:
            self.stdout.write(f'... dan {len(context) - 10} queries lainnya')
        
        self.print_analysis(
            query_count=len(context),
            is_optimized=False,
            explanation='❌ N+1 Problem: Setiap enrollment membuat multiple queries untuk course, instructor, dan progress'
        )

    def demo_optimized_enrollment(self):
        """Demo optimized enrollment listing"""
        self.stdout.write('\n' + self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('DEMO 4: OPTIMIZED - Student Dashboard with Prefetch'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        with CaptureQueriesContext(connection) as context:
            # Gunakan for_student_dashboard() custom manager
            enrollments = Enrollment.objects.for_student_dashboard()
            for enrollment in enrollments:
                course_title = enrollment.course.title
                instructor = enrollment.course.instructor.username
                progress_items = list(enrollment.progress.all())
                progress_count = len(progress_items)

        self.stdout.write(f'Total Queries: {len(context)} ✓\n')
        for i, query in enumerate(context, 1):
            self.stdout.write(f'{i}. {query["sql"][:100]}...')
        
        self.print_analysis(
            query_count=len(context),
            is_optimized=True,
            explanation='✓ Optimized: select_related() untuk course relationships, prefetch_related() untuk progress items'
        )

    def print_analysis(self, query_count, is_optimized, explanation):
        """Print analysis summary"""
        self.stdout.write('\n' + self.style.HTTP_INFO('Analysis:'))
        self.stdout.write(f'  Query Count: {query_count}')
        self.stdout.write(f'  Status: {"✓ OPTIMAL" if is_optimized else "❌ PROBLEMATIC"}')
        self.stdout.write(f'  {explanation}')
        self.stdout.write('')
