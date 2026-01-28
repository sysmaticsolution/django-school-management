"""
Django base settings for School Management System.
"""
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# Application definition
DJANGO_APPS = [
    'jazzmin',  # Must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.core',
    'apps.academics',
    'apps.students',
    'apps.staff',
    'apps.fees',
    'apps.attendance',
    'apps.examinations',
    'apps.transport',
    'apps.library',
    'apps.communication',
    'apps.inventory',
    'apps.hostel',
    'apps.reports',
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csp.ContentSecurityPolicyMiddleware',  # Django 6.0 CSP
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csp',  # Django 6.0 CSP nonces
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database - SQLite by default
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'  # Indian Standard Time

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# DJANGO 6.0 FEATURES
# =============================================================================

# Content Security Policy (CSP) - Django 6.0
# Protects against XSS attacks by declaring trusted content sources
from django.utils.csp import CSP

SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, CSP.NONCE, "https://cdn.jsdelivr.net"],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE, "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
    "img-src": [CSP.SELF, "data:", "https:"],
    "font-src": [CSP.SELF, "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
    "connect-src": [CSP.SELF],
    "frame-ancestors": [CSP.SELF],
}

# Background Tasks - Django 6.0
# For async operations like sending emails, generating reports, etc.
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.ImmediateBackend",
    }
}

# =============================================================================
# REST FRAMEWORK SETTINGS
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'School Management System API',
    'DESCRIPTION': 'REST API for Indian School Management System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentication endpoints'},
        {'name': 'Students', 'description': 'Student management'},
        {'name': 'Staff', 'description': 'Staff management'},
        {'name': 'Academics', 'description': 'Classes, Sections, Subjects'},
        {'name': 'Fees', 'description': 'Fee management'},
        {'name': 'Attendance', 'description': 'Attendance tracking'},
        {'name': 'Reports', 'description': 'Reports and exports'},
    ],
}

# =============================================================================
# JAZZMIN SETTINGS
# =============================================================================

JAZZMIN_SETTINGS = {
    # Title
    "site_title": "School Admin",
    "site_header": "School Management",
    "site_brand": "SMS",
    "site_logo": None,
    "login_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    
    # Welcome text
    "welcome_sign": "Welcome to School Management System",
    
    # Copyright
    "copyright": "Indian School Management System",
    
    # Search models
    "search_model": ["accounts.User", "students.Student"],
    
    # User avatar
    "user_avatar": None,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Dashboard", "url": "/", "new_window": False},
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Order of apps in sidebar
    "order_with_respect_to": [
        "accounts",
        "core",
        "academics",
        "students",
        "staff",
        "fees",
        "attendance",
        "examinations",
        "transport",
        "library",
        "communication",
        "inventory",
        "hostel",
        "reports",
    ],
    
    # Icons - using Font Awesome 5
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "accounts": "fas fa-user-shield",
        "accounts.User": "fas fa-user",
        "core": "fas fa-cog",
        "core.SchoolProfile": "fas fa-school",
        "core.AcademicYear": "fas fa-calendar-alt",
        "academics": "fas fa-graduation-cap",
        "academics.Standard": "fas fa-layer-group",
        "academics.Section": "fas fa-th-large",
        "academics.Subject": "fas fa-book",
        "students": "fas fa-user-graduate",
        "students.Student": "fas fa-user-graduate",
        "staff": "fas fa-chalkboard-teacher",
        "staff.Teacher": "fas fa-chalkboard-teacher",
        "staff.Staff": "fas fa-id-badge",
        "staff.Department": "fas fa-building",
        "staff.Designation": "fas fa-user-tag",
        # Fee Management
        "fees": "fas fa-rupee-sign",
        "fees.FeeCategory": "fas fa-tags",
        "fees.FeeStructure": "fas fa-file-invoice",
        "fees.FeeDiscount": "fas fa-percent",
        "fees.StudentFee": "fas fa-file-invoice-dollar",
        "fees.FeePayment": "fas fa-money-bill-wave",
        # Attendance
        "attendance": "fas fa-calendar-check",
        "attendance.StudentAttendance": "fas fa-user-check",
        "attendance.SubjectAttendance": "fas fa-book-reader",
        "attendance.AttendanceSummary": "fas fa-chart-pie",
        "attendance.LeaveRequest": "fas fa-envelope-open-text",
        "attendance.StaffAttendance": "fas fa-id-card",
        # Examinations
        "examinations": "fas fa-edit",
        "examinations.ExamType": "fas fa-clipboard-list",
        "examinations.Exam": "fas fa-file-alt",
        "examinations.ExamSchedule": "fas fa-calendar-day",
        "examinations.ExamResult": "fas fa-poll",
        "examinations.ReportCard": "fas fa-scroll",
        # Transport
        "transport": "fas fa-bus",
        "transport.Vehicle": "fas fa-bus-alt",
        "transport.Driver": "fas fa-id-card-alt",
        "transport.Route": "fas fa-route",
        "transport.RouteStop": "fas fa-map-marker-alt",
        "transport.StudentTransport": "fas fa-user-friends",
        # Library
        "library": "fas fa-book-open",
        "library.Book": "fas fa-book",
        "library.BookCategory": "fas fa-folder",
        "library.BookRack": "fas fa-archive",
        "library.LibraryMember": "fas fa-address-card",
        "library.BookIssue": "fas fa-exchange-alt",
        "library.LibrarySetting": "fas fa-cogs",
        # Communication
        "communication": "fas fa-comments",
        "communication.Notice": "fas fa-bullhorn",
        "communication.SMSLog": "fas fa-sms",
        "communication.EmailLog": "fas fa-envelope",
        "communication.MessageTemplate": "fas fa-file-signature",
        "communication.Notification": "fas fa-bell",
        "communication.Event": "fas fa-calendar-week",
        # Inventory
        "inventory": "fas fa-boxes",
        "inventory.ItemCategory": "fas fa-folder-open",
        "inventory.StoreLocation": "fas fa-warehouse",
        "inventory.Vendor": "fas fa-truck",
        "inventory.Item": "fas fa-cube",
        "inventory.PurchaseOrder": "fas fa-file-invoice",
        "inventory.StockTransaction": "fas fa-exchange-alt",
        "inventory.Asset": "fas fa-laptop",
        # Hostel
        "hostel": "fas fa-bed",
        "hostel.Hostel": "fas fa-hotel",
        "hostel.HostelRoom": "fas fa-door-open",
        "hostel.HostelAllocation": "fas fa-user-check",
        "hostel.MessMenu": "fas fa-utensils",
        "hostel.HostelVisitor": "fas fa-user-friends",
        "hostel.LeavePass": "fas fa-ticket-alt",
        # Reports
        "reports": "fas fa-chart-line",
        "reports.ReportCategory": "fas fa-folder",
        "reports.ReportTemplate": "fas fa-file-code",
        "reports.SavedReport": "fas fa-save",
        "reports.ScheduledReport": "fas fa-clock",
        "reports.ReportExecution": "fas fa-history",
        "reports.DashboardWidget": "fas fa-th-large",
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
