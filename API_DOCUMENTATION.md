# Simple LMS REST API

REST API lengkap untuk Simple Learning Management System menggunakan Django Ninja dengan JWT authentication dan role-based authorization.

## Features

- ✅ JWT Authentication (access + refresh tokens)
- ✅ Role-Based Access Control (Student, Instructor, Admin)
- ✅ CRUD operations untuk Courses
- ✅ Enrollment system
- ✅ Pydantic schema validation
- ✅ Auto-generated Swagger documentation
- ✅ Docker containerized

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update profile

### Courses (Public)
- `GET /api/v1/courses/` - List courses with filters (search, price range)
- `GET /api/v1/courses/{id}` - Course detail with contents

### Courses (Protected)
- `POST /api/v1/courses/` - Create course (Instructor only)
- `PATCH /api/v1/courses/{id}` - Update course (Owner or Admin)
- `DELETE /api/v1/courses/{id}` - Delete course (Admin only)

### Enrollments
- `POST /api/v1/enrollments/` - Enroll to course (Student only)
- `GET /api/v1/enrollments/my-courses` - My enrolled courses

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Load fixtures:
```bash
python manage.py loaddata initial_data
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run server:
```bash
python manage.py runserver
```

## API Documentation

Access Swagger UI at: `http://localhost:8000/api/v1/docs`

## Authentication

1. Register a user with role (student/instructor/admin)
2. Login to get access and refresh tokens
3. Include access token in Authorization header: `Bearer <token>`
4. Use refresh token to get new access token when expired

## Roles & Permissions

- **Student**: Can enroll to courses, view enrolled courses
- **Instructor**: Can create and update own courses
- **Admin**: Can delete any course, full access

## Testing with Postman

Import the collection from `postman_collection.json` (create if needed).

Example requests:
- Register: POST /api/v1/auth/register with JSON body
- Login: POST /api/v1/auth/login
- List courses: GET /api/v1/courses/ with Authorization header

## Docker

```bash
# Build and run
docker-compose up --build

# Access API
curl http://localhost:8000/api/v1/hello/
```

## Models

- User (built-in) + Profile (role)
- Course (name, description, price, teacher)
- CourseMember (enrollment with role)
- CourseContent (lessons)
- Comment (discussions)

## Technologies

- Django 4.2+
- Django Ninja 1.1
- Django REST Framework Simple JWT
- Pydantic for validation
- PostgreSQL
- Docker