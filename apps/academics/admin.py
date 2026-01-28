"""
Admin configuration for academics app.
"""
from django.contrib import admin
from .models import Standard, Section, Subject


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    """Standard/Class admin configuration."""
    
    list_display = ['name', 'numeric_value', 'section_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    ordering = ['numeric_value']
    
    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Sections'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Section admin configuration."""
    
    list_display = ['full_name', 'standard', 'name', 'class_teacher', 'room_number', 'capacity', 'is_active']
    list_filter = ['standard', 'is_active']
    search_fields = ['name', 'standard__name', 'room_number']
    list_editable = ['is_active']
    autocomplete_fields = ['standard', 'class_teacher']
    
    fieldsets = (
        (None, {
            'fields': ('standard', 'name')
        }),
        ('Details', {
            'fields': ('class_teacher', 'room_number', 'capacity')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Subject admin configuration."""
    
    list_display = ['code', 'name', 'subject_type', 'total_marks', 'passing_percentage', 'is_optional', 'is_active']
    list_filter = ['subject_type', 'is_optional', 'is_active', 'standards']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    filter_horizontal = ['standards']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'subject_type', 'description')
        }),
        ('Marks Configuration', {
            'fields': (('max_theory_marks', 'max_practical_marks'), 'passing_percentage')
        }),
        ('Class Assignment', {
            'fields': ('standards', 'is_optional')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
