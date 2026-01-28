# AI Coding Guide - Indian School Management System

> **Purpose**: This document provides AI assistants with complete context, coding standards, and implementation details to maintain consistency across the codebase.

---

## 🏗️ Project Overview

**Project Name**: Indian School Management System  
**Framework**: Django 5.x with Python 3.12+  
**Admin Theme**: Jazzmin  
**Database**: PostgreSQL (SQLite for development)  

---

## 📁 Project Structure

```
django-school-management/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── FEATURES.md
├── AI_CODING_GUIDE.md
│
├── config/                     # Project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Common settings
│   │   ├── development.py     # Dev settings
│   │   └── production.py      # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                       # Django applications
│   ├── __init__.py
│   ├── accounts/              # User & Authentication
│   ├── core/                  # School settings, Academic year
│   ├── students/              # Student management
│   ├── staff/                 # Teacher & Staff management
│   ├── academics/             # Classes, Subjects, Timetable
│   ├── attendance/            # Attendance tracking
│   ├── examinations/          # Exams & Results
│   ├── fees/                  # Fee management
│   ├── transport/             # Transport management
│   ├── library/               # Library management
│   ├── hostel/                # Hostel management
│   ├── communication/         # Notifications & Messaging
│   └── reports/               # Reports & Analytics
│
├── static/                    # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                 # Global templates
│   ├── base.html
│   ├── includes/
│   └── components/
│
└── media/                     # User uploads
    ├── students/
    ├── staff/
    └── documents/
```

---

## 🎯 Coding Standards

### Django App Structure
Each app should follow this structure:
```
apps/appname/
├── __init__.py
├── admin.py           # Admin configuration with Jazzmin
├── apps.py            # App configuration
├── models.py          # Database models
├── views.py           # Views (or views/ directory for larger apps)
├── urls.py            # URL patterns
├── forms.py           # Django forms
├── serializers.py     # DRF serializers (if needed)
├── signals.py         # Django signals
├── managers.py        # Custom model managers
├── utils.py           # Utility functions
├── constants.py       # App-specific constants
├── tests/             # Test directory
│   ├── __init__.py
│   ├── test_models.py
│   └── test_views.py
├── templates/appname/ # App templates
└── migrations/        # Database migrations
```

### Naming Conventions
```python
# Models: PascalCase, singular
class Student(models.Model):
    pass

class AcademicYear(models.Model):
    pass

# Fields: snake_case
first_name = models.CharField()
date_of_birth = models.DateField()
created_at = models.DateTimeField()

# Foreign Keys: Use related model name
student = models.ForeignKey(Student, ...)
academic_year = models.ForeignKey(AcademicYear, ...)

# Many-to-Many: Plural
subjects = models.ManyToManyField(Subject)
teachers = models.ManyToManyField(Teacher)

# Boolean fields: Start with is_, has_, can_
is_active = models.BooleanField()
has_transport = models.BooleanField()
can_login = models.BooleanField()
```

---

## 📊 Core Models Reference

### User Model (apps/accounts/models.py)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model with role-based access"""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        PRINCIPAL = 'principal', 'Principal'
        TEACHER = 'teacher', 'Teacher'
        STAFF = 'staff', 'Staff'
        PARENT = 'parent', 'Parent'
        STUDENT = 'student', 'Student'
    
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=15, blank=True)
    aadhaar_number = models.CharField(max_length=12, blank=True)  # Indian Aadhaar
    
    class Meta:
        db_table = 'users'
```

### Academic Year (apps/core/models.py)
```python
class AcademicYear(models.Model):
    """Indian academic year April to March"""
    
    name = models.CharField(max_length=20)  # e.g., "2024-25"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'academic_years'
        ordering = ['-start_date']
```

### Class/Standard (apps/academics/models.py)
```python
class Standard(models.Model):
    """School class/standard (1st to 12th)"""
    
    name = models.CharField(max_length=20)  # e.g., "Class 10"
    numeric_value = models.PositiveIntegerField()  # 1-12
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'standards'
        ordering = ['numeric_value']


class Section(models.Model):
    """Class sections (A, B, C, etc.)"""
    
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)  # A, B, C
    class_teacher = models.ForeignKey('staff.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=40)
    
    class Meta:
        db_table = 'sections'
        unique_together = ['standard', 'name']
```

### Student (apps/students/models.py)
```python
class Student(models.Model):
    """Student master record"""
    
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
    
    class BloodGroup(models.TextChoices):
        A_POSITIVE = 'A+', 'A+'
        A_NEGATIVE = 'A-', 'A-'
        B_POSITIVE = 'B+', 'B+'
        B_NEGATIVE = 'B-', 'B-'
        AB_POSITIVE = 'AB+', 'AB+'
        AB_NEGATIVE = 'AB-', 'AB-'
        O_POSITIVE = 'O+', 'O+'
        O_NEGATIVE = 'O-', 'O-'
    
    class Category(models.TextChoices):
        GENERAL = 'general', 'General'
        OBC = 'obc', 'OBC'
        SC = 'sc', 'SC'
        ST = 'st', 'ST'
        EWS = 'ews', 'EWS'
    
    # Basic Info
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    admission_number = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices, blank=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True)
    
    # Indian-specific
    aadhaar_number = models.CharField(max_length=12, blank=True)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.GENERAL)
    religion = models.CharField(max_length=50, blank=True)
    caste = models.CharField(max_length=100, blank=True)
    mother_tongue = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=50, default='Indian')
    
    # Contact
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    # Parent/Guardian Info
    father_name = models.CharField(max_length=100)
    father_phone = models.CharField(max_length=15, blank=True)
    father_occupation = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100)
    mother_phone = models.CharField(max_length=15, blank=True)
    mother_occupation = models.CharField(max_length=100, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    
    # Academic
    admission_date = models.DateField()
    current_section = models.ForeignKey('academics.Section', on_delete=models.SET_NULL, null=True)
    previous_school = models.CharField(max_length=200, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_rte = models.BooleanField(default=False)  # Right to Education
    has_transport = models.BooleanField(default=False)
    has_hostel = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['current_section', 'roll_number']
    
    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

---

## 🎨 Jazzmin Admin Configuration

```python
# config/settings/base.py

JAZZMIN_SETTINGS = {
    # Title
    "site_title": "School Admin",
    "site_header": "School Management",
    "site_brand": "SMS",
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/favicon.ico",
    
    # Welcome text
    "welcome_sign": "Welcome to School Management System",
    
    # Copyright
    "copyright": "School Management System",
    
    # Search model
    "search_model": ["accounts.User", "students.Student", "staff.Teacher"],
    
    # User avatar
    "user_avatar": None,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Icons - using Font Awesome
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.User": "fas fa-user",
        "students.Student": "fas fa-user-graduate",
        "staff.Teacher": "fas fa-chalkboard-teacher",
        "academics.Standard": "fas fa-school",
        "academics.Subject": "fas fa-book",
        "attendance.Attendance": "fas fa-calendar-check",
        "examinations.Exam": "fas fa-edit",
        "fees.Fee": "fas fa-rupee-sign",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Related Modal
    "related_modal_active": True,
    
    # UI Customization
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Theme
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "accounts.User": "collapsible",
        "students.Student": "collapsible",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "minty",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
```

---

## 📋 Admin Model Registration Pattern

```python
# apps/students/admin.py

from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'full_name', 'current_section', 'father_name', 'phone', 'is_active']
    list_filter = ['current_section__standard', 'current_section', 'gender', 'category', 'is_active', 'is_rte']
    search_fields = ['admission_number', 'first_name', 'last_name', 'father_name', 'phone', 'aadhaar_number']
    list_editable = ['is_active']
    list_per_page = 25
    date_hierarchy = 'admission_date'
    ordering = ['current_section', 'roll_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('admission_number', 'roll_number', ('first_name', 'last_name'), 
                      ('date_of_birth', 'gender'), ('blood_group', 'photo'))
        }),
        ('Indian Specific', {
            'fields': (('aadhaar_number', 'category'), ('religion', 'caste'), 
                      ('mother_tongue', 'nationality')),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('address', ('city', 'state', 'pincode'), ('phone', 'email'))
        }),
        ('Parent/Guardian Details', {
            'fields': (('father_name', 'father_phone', 'father_occupation'),
                      ('mother_name', 'mother_phone', 'mother_occupation'),
                      ('guardian_name', 'guardian_phone', 'guardian_relation'))
        }),
        ('Academic Information', {
            'fields': (('admission_date', 'current_section'), 'previous_school')
        }),
        ('Status', {
            'fields': (('is_active', 'is_rte'), ('has_transport', 'has_hostel'))
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'current_section']
    autocomplete_fields = ['current_section']
```

---

## 🇮🇳 Indian-Specific Constants

```python
# apps/core/constants.py

# Indian States and Union Territories
INDIAN_STATES = [
    ('AN', 'Andaman and Nicobar Islands'),
    ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'),
    ('AS', 'Assam'),
    ('BR', 'Bihar'),
    ('CH', 'Chandigarh'),
    ('CT', 'Chhattisgarh'),
    ('DL', 'Delhi'),
    ('GA', 'Goa'),
    ('GJ', 'Gujarat'),
    ('HR', 'Haryana'),
    ('HP', 'Himachal Pradesh'),
    ('JK', 'Jammu and Kashmir'),
    ('JH', 'Jharkhand'),
    ('KA', 'Karnataka'),
    ('KL', 'Kerala'),
    ('LA', 'Ladakh'),
    ('LD', 'Lakshadweep'),
    ('MP', 'Madhya Pradesh'),
    ('MH', 'Maharashtra'),
    ('MN', 'Manipur'),
    ('ML', 'Meghalaya'),
    ('MZ', 'Mizoram'),
    ('NL', 'Nagaland'),
    ('OR', 'Odisha'),
    ('PY', 'Puducherry'),
    ('PB', 'Punjab'),
    ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'),
    ('TN', 'Tamil Nadu'),
    ('TG', 'Telangana'),
    ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'),
    ('WB', 'West Bengal'),
]

# Indian Board Types
BOARD_TYPES = [
    ('cbse', 'CBSE - Central Board of Secondary Education'),
    ('icse', 'ICSE - Indian Certificate of Secondary Education'),
    ('state', 'State Board'),
    ('ib', 'IB - International Baccalaureate'),
    ('igcse', 'IGCSE - Cambridge'),
]

# Grading Systems
CBSE_GRADES = [
    ('A1', 'A1 (91-100)'),
    ('A2', 'A2 (81-90)'),
    ('B1', 'B1 (71-80)'),
    ('B2', 'B2 (61-70)'),
    ('C1', 'C1 (51-60)'),
    ('C2', 'C2 (41-50)'),
    ('D', 'D (33-40)'),
    ('E', 'E (Below 33)'),
]

# Fee Types
FEE_TYPES = [
    ('admission', 'Admission Fee'),
    ('tuition', 'Tuition Fee'),
    ('exam', 'Examination Fee'),
    ('transport', 'Transport Fee'),
    ('hostel', 'Hostel Fee'),
    ('library', 'Library Fee'),
    ('lab', 'Laboratory Fee'),
    ('sports', 'Sports Fee'),
    ('computer', 'Computer Fee'),
    ('annual', 'Annual Charges'),
    ('development', 'Development Fee'),
    ('misc', 'Miscellaneous'),
]

# Common Indian Religions
RELIGIONS = [
    ('hinduism', 'Hinduism'),
    ('islam', 'Islam'),
    ('christianity', 'Christianity'),
    ('sikhism', 'Sikhism'),
    ('buddhism', 'Buddhism'),
    ('jainism', 'Jainism'),
    ('other', 'Other'),
]
```

---

## 🔐 Permission Groups

```python
# Create these groups during initial setup

PERMISSION_GROUPS = {
    'Administrator': [
        # Full access to everything
    ],
    'Principal': [
        'view_student', 'add_student', 'change_student',
        'view_teacher', 'add_teacher', 'change_teacher',
        'view_attendance', 'view_fee', 'view_exam',
        # All view + most edit permissions
    ],
    'Teacher': [
        'view_student',
        'view_attendance', 'add_attendance', 'change_attendance',
        'view_exam', 'add_examresult', 'change_examresult',
        # Limited to own class/subjects
    ],
    'Accountant': [
        'view_fee', 'add_fee', 'change_fee',
        'add_feepayment', 'change_feepayment',
        # Only fee-related
    ],
    'Librarian': [
        'view_book', 'add_book', 'change_book',
        'add_bookissue', 'change_bookissue',
        # Only library-related
    ],
}
```

---

## 📝 Common Queries & Methods

```python
# Get all active students in a class
Student.objects.filter(
    is_active=True,
    current_section__standard__numeric_value=10
)

# Get current academic year
AcademicYear.objects.get(is_current=True)

# Get students with pending fees
from django.db.models import Sum, F
Student.objects.annotate(
    total_due=Sum('fees__amount') - Sum('fee_payments__amount')
).filter(total_due__gt=0)

# Get attendance percentage for a student
total_days = Attendance.objects.filter(student=student, academic_year=current_year).count()
present_days = Attendance.objects.filter(student=student, academic_year=current_year, status='present').count()
percentage = (present_days / total_days) * 100 if total_days > 0 else 0
```

---

## 🚀 Commands to Remember

```bash
# Create new Django app in apps directory
python manage.py startapp appname apps/appname

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Run tests
python manage.py test apps.appname

# Create initial data fixtures
python manage.py dumpdata appname > fixtures/appname.json
python manage.py loaddata fixtures/appname.json
```

---

## ⚠️ Important Notes for AI Assistants

1. **Always use the apps/ directory** for new Django applications
2. **Follow the model patterns** defined in this guide
3. **Use db_table** in Meta class for consistent naming
4. **Include Indian-specific fields** like Aadhaar, Category, etc.
5. **Always add fieldsets** in admin for better organization
6. **Use TextChoices** for status fields with limited options
7. **Add timestamps** (created_at, updated_at) to all models
8. **Use related_name** for all ForeignKey fields
9. **Keep the Jazzmin configuration** updated with new models
10. **Write docstrings** for all models and complex methods

---

## 📚 Reference Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Jazzmin Documentation](https://django-jazzmin.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [CBSE Grading System](https://www.cbse.gov.in/)
