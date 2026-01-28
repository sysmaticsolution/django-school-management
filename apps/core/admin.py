"""
Admin configuration for core app.
"""
from django.contrib import admin
from .models import SchoolProfile, AcademicYear


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    """School profile admin configuration."""
    
    list_display = ['name', 'city', 'state', 'board_type', 'principal_name', 'is_active']
    list_filter = ['state', 'board_type', 'is_active']
    search_fields = ['name', 'city', 'email', 'affiliation_number', 'udise_code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'logo')
        }),
        ('Contact Details', {
            'fields': ('address', ('city', 'state', 'pincode'), ('phone', 'alternate_phone'), ('email', 'website'))
        }),
        ('Affiliation', {
            'fields': ('board_type', 'affiliation_number', 'udise_code')
        }),
        ('Principal', {
            'fields': ('principal_name', 'principal_signature')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'bank_account_number', 'bank_ifsc_code'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    """Academic year admin configuration."""
    
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'is_admission_open']
    list_filter = ['is_current', 'is_admission_open']
    search_fields = ['name']
    list_editable = ['is_current', 'is_admission_open']
    ordering = ['-start_date']
    
    fieldsets = (
        (None, {
            'fields': ('name', ('start_date', 'end_date'))
        }),
        ('Status', {
            'fields': (('is_current', 'is_admission_open'),)
        }),
    )
