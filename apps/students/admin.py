"""
Admin configuration for students app.
"""
from django.contrib import admin
from .models import Student, StudentDocument


class StudentDocumentInline(admin.TabularInline):
    """Inline for student documents."""
    model = StudentDocument
    extra = 1
    fields = ['document_type', 'document_name', 'file']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student admin configuration with comprehensive fieldsets."""
    
    list_display = [
        'admission_number', 
        'full_name', 
        'class_and_section', 
        'father_name', 
        'phone', 
        'category',
        'is_active'
    ]
    list_filter = [
        'current_section__standard', 
        'current_section', 
        'gender', 
        'category', 
        'is_active', 
        'is_rte',
        'has_transport',
        'has_hostel'
    ]
    search_fields = [
        'admission_number', 
        'first_name', 
        'last_name', 
        'father_name',
        'mother_name',
        'phone', 
        'father_phone',
        'aadhaar_number'
    ]
    list_editable = ['is_active']
    list_per_page = 25
    date_hierarchy = 'admission_date'
    ordering = ['current_section', 'roll_number']
    autocomplete_fields = ['current_section', 'admission_class']
    raw_id_fields = ['user']
    inlines = [StudentDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'admission_number', 
                'roll_number',
                ('first_name', 'middle_name', 'last_name'),
                ('date_of_birth', 'gender', 'blood_group'),
                'photo'
            )
        }),
        ('Indian Specific', {
            'fields': (
                'aadhaar_number',
                ('category', 'religion'),
                ('caste', 'sub_caste'),
                ('mother_tongue', 'nationality')
            ),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': (
                'address',
                ('city', 'district'),
                ('state', 'pincode'),
                ('phone', 'alternate_phone'),
                'email'
            )
        }),
        ("Father's Details", {
            'fields': (
                ('father_name', 'father_phone'),
                ('father_email', 'father_aadhaar'),
                ('father_occupation', 'father_qualification'),
                'father_annual_income'
            )
        }),
        ("Mother's Details", {
            'fields': (
                ('mother_name', 'mother_phone'),
                ('mother_email', 'mother_aadhaar'),
                ('mother_occupation', 'mother_qualification')
            ),
            'classes': ('collapse',)
        }),
        ('Guardian Details', {
            'fields': (
                ('guardian_name', 'guardian_phone'),
                'guardian_relation',
                'guardian_address'
            ),
            'classes': ('collapse',)
        }),
        ('Academic Information', {
            'fields': (
                ('admission_date', 'current_section'),
                'admission_class',
                ('previous_school', 'previous_class'),
                'tc_number'
            )
        }),
        ('Health Information', {
            'fields': (
                'medical_conditions',
                'allergies',
                'emergency_contact'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Services', {
            'fields': (
                'is_active',
                ('is_rte', 'has_scholarship'),
                ('has_transport', 'has_hostel')
            )
        }),
        ('User Account', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    """Student document admin."""
    
    list_display = ['student', 'document_type', 'document_name', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number', 'document_name']
    autocomplete_fields = ['student']
