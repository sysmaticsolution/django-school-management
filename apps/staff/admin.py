"""
Admin configuration for staff app.
"""
from django.contrib import admin
from .models import Department, Designation, Teacher, Staff


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Department admin configuration."""
    
    list_display = ['name', 'code', 'head', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    autocomplete_fields = ['head']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """Designation admin configuration."""
    
    list_display = ['name', 'category', 'pay_grade', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'pay_grade']
    list_editable = ['is_active']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Teacher admin configuration."""
    
    list_display = [
        'employee_id', 
        'full_name', 
        'department', 
        'designation',
        'phone', 
        'date_of_joining',
        'is_active'
    ]
    list_filter = [
        'department', 
        'designation', 
        'employment_type',
        'is_active',
        'date_of_joining'
    ]
    search_fields = [
        'employee_id', 
        'first_name', 
        'last_name', 
        'phone',
        'email',
        'aadhaar_number'
    ]
    list_editable = ['is_active']
    list_per_page = 25
    date_hierarchy = 'date_of_joining'
    filter_horizontal = ['subjects']
    autocomplete_fields = ['department', 'designation']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'employee_id',
                ('first_name', 'last_name'),
                ('date_of_birth', 'gender', 'blood_group'),
                'photo'
            )
        }),
        ('Indian Specific', {
            'fields': (
                ('aadhaar_number', 'pan_number'),
                ('category', 'religion')
            ),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': (
                'address',
                ('city', 'state', 'pincode'),
                ('phone', 'alternate_phone'),
                'email',
                ('emergency_contact', 'emergency_contact_name')
            )
        }),
        ('Professional Information', {
            'fields': (
                ('department', 'designation'),
                'subjects',
                ('qualification', 'specialization'),
                'experience_years'
            )
        }),
        ('Employment Details', {
            'fields': (
                ('date_of_joining', 'date_of_leaving'),
                'employment_type'
            )
        }),
        ('Bank Details', {
            'fields': (
                'bank_name',
                ('bank_account_number', 'bank_ifsc_code')
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('User Account', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Non-teaching staff admin configuration."""
    
    list_display = [
        'employee_id', 
        'full_name', 
        'department', 
        'designation',
        'phone', 
        'date_of_joining',
        'is_active'
    ]
    list_filter = [
        'department', 
        'designation', 
        'employment_type',
        'is_active'
    ]
    search_fields = [
        'employee_id', 
        'first_name', 
        'last_name', 
        'phone',
        'aadhaar_number'
    ]
    list_editable = ['is_active']
    autocomplete_fields = ['department', 'designation']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'employee_id',
                ('first_name', 'last_name'),
                ('date_of_birth', 'gender', 'blood_group'),
                'photo'
            )
        }),
        ('ID Documents', {
            'fields': (('aadhaar_number', 'pan_number'),),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': (
                'address',
                ('city', 'state', 'pincode'),
                ('phone', 'email')
            )
        }),
        ('Employment Details', {
            'fields': (
                ('department', 'designation'),
                ('date_of_joining', 'date_of_leaving'),
                'employment_type'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('User Account', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
