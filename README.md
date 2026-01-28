# Indian School Management System

A comprehensive Django-based school management system designed for Indian schools, featuring:
- CBSE/ICSE/State Board support
- Indian-specific fields (Aadhaar, Category, RTE)
- Modern admin interface with Jazzmin theme
- Role-based access control

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python 3.12+ and pip
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

### Installation
```bash
# Clone/navigate to the project
cd django-school-management

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

### Access the Admin
- URL: http://127.0.0.1:8000/admin/
- Login with your superuser credentials

## 📁 Project Structure

```
django-school-management/
├── config/                 # Django settings & configuration
│   ├── settings/
│   │   ├── base.py        # Common settings + Jazzmin config
│   │   └── development.py # Development settings
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Django applications
│   ├── accounts/          # User authentication & roles
│   ├── core/              # School profile & academic year
│   ├── academics/         # Classes, sections, subjects
│   ├── students/          # Student management
│   └── staff/             # Teacher & staff management
├── manage.py
└── requirements.txt
```

## 👥 User Roles

| Role | Access Level |
|------|--------------|
| Admin | Full system access |
| Principal | School-wide management |
| Teacher | Class & subject management |
| Accountant | Fee management |
| Librarian | Library management |
| Parent | Child's information |
| Student | Own information |

## 📚 Features

### ✅ Phase 1 - Foundation
- Custom User model with roles (Admin, Principal, Teacher, Staff, Parent, Student)
- School Profile configuration
- Academic Year management (April-March)
- Class/Section management
- Subject management with CBSE syllabus support
- Student management (40+ Indian-specific fields)
- Teacher/Staff management with qualifications

### ✅ Phase 2 - Core Operations
- Fee Management (categories, structures, discounts, payments)
- Attendance Tracking (daily, subject-wise, staff)
- Leave Request management with approval workflow
- Examination Management (exams, schedules, marks)
- Auto-grading (CBSE A1-E system)
- Report Card generation with rankings

### ✅ Phase 3 - Extended Features
- Transport Management (vehicles, routes, drivers, GPS)
- Library Management (books, issues, fines)
- Communication (notices, SMS, email, events)
- Message Templates with placeholders
- In-app Notifications

### ✅ Phase 4 - Advanced Features
- Inventory Management (items, vendors, purchase orders)
- Asset Tracking with depreciation
- Hostel Management (rooms, allocations, mess menu)
- Visitor Log and Leave Pass system
- Reports & Analytics with scheduling
- Dashboard Widgets

## 🇮🇳 Indian-Specific Features

- **Aadhaar Integration**: Store Aadhaar numbers for students and staff
- **Category/Reservation**: Support for General, OBC, SC, ST, EWS categories
- **RTE Compliance**: Right to Education admission tracking
- **Board Support**: CBSE, ICSE, State Board grading systems
- **Academic Year**: April-March calendar (Indian system)
- **State Data**: All Indian states and UTs included
- **GST Support**: Vendor GSTIN tracking for purchases

## 📄 Documentation

- [FEATURES.md](FEATURES.md) - Complete feature list
- [AI_CODING_GUIDE.md](AI_CODING_GUIDE.md) - Coding standards for AI assistants

## 🛠️ Tech Stack

- **Backend**: Django 6.0.1 (Latest)
- **Admin Theme**: Jazzmin
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Python**: 3.12+
- **Django 6.0 Features**:
  - Content Security Policy (CSP)
  - Background Tasks framework
  - Template Partials support

## 📁 Project Structure (14 Apps)

```
apps/
├── accounts/          # User authentication & roles
├── core/              # School profile, academic year, tasks
├── academics/         # Classes, sections, subjects
├── students/          # Student management
├── staff/             # Teacher & staff management
├── fees/              # Fee management
├── attendance/        # Attendance tracking
├── examinations/      # Exams & results
├── transport/         # Transport management
├── library/           # Library management
├── communication/     # Notices, SMS, email
├── inventory/         # Inventory & assets
├── hostel/            # Hostel management
└── reports/           # Reports & analytics
```

## 📝 License

MIT License

