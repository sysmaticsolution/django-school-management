"""
Admin configuration for reports app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ReportCategory, ReportTemplate, SavedReport,
    ScheduledReport, ReportExecution, DashboardWidget
)


@admin.register(ReportCategory)
class ReportCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'icon_preview', 'order', 'templates_count']
    list_editable = ['order']
    search_fields = ['name', 'code']
    
    def icon_preview(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
    icon_preview.short_description = 'Icon'
    
    def templates_count(self, obj):
        return obj.templates.count()
    templates_count.short_description = 'Templates'


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'category',
        'report_type',
        'export_formats',
        'is_active'
    ]
    list_filter = ['report_type', 'category', 'is_active']
    search_fields = ['name', 'code', 'description']
    autocomplete_fields = ['category']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Info', {
            'fields': (('name', 'code'), 'description', ('category', 'report_type'))
        }),
        ('Configuration', {
            'fields': ('query_config', 'available_filters', 'columns'),
            'classes': ('collapse',)
        }),
        ('Export Options', {
            'fields': (('supports_pdf', 'supports_excel', 'supports_csv'),)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def export_formats(self, obj):
        formats = []
        if obj.supports_pdf:
            formats.append('PDF')
        if obj.supports_excel:
            formats.append('Excel')
        if obj.supports_csv:
            formats.append('CSV')
        return ', '.join(formats)
    export_formats.short_description = 'Formats'


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'created_by', 'is_shared', 'updated_at']
    list_filter = ['is_shared', 'template__report_type', 'created_by']
    search_fields = ['name', 'template__name']
    autocomplete_fields = ['template', 'created_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'saved_report',
        'frequency',
        'run_time',
        'output_format',
        'is_active',
        'last_run',
        'next_run'
    ]
    list_filter = ['frequency', 'output_format', 'is_active']
    search_fields = ['name', 'saved_report__name']
    autocomplete_fields = ['saved_report', 'created_by']
    readonly_fields = ['last_run', 'next_run']
    
    fieldsets = (
        ('Report', {
            'fields': ('name', 'saved_report')
        }),
        ('Schedule', {
            'fields': ('frequency', 'run_time', ('day_of_week', 'day_of_month'))
        }),
        ('Output', {
            'fields': ('output_format', 'email_recipients')
        }),
        ('Status', {
            'fields': ('is_active', ('last_run', 'next_run'))
        }),
    )


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'template',
        'status_colored',
        'started_at',
        'execution_time_display',
        'row_count',
        'executed_by'
    ]
    list_filter = ['status', 'template', 'started_at']
    search_fields = ['template__name']
    readonly_fields = [
        'template', 'saved_report', 'scheduled_report', 'parameters',
        'status', 'started_at', 'completed_at', 'output_file',
        'row_count', 'error_message', 'executed_by', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def status_colored(self, obj):
        colors = {
            'pending': 'gray',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def execution_time_display(self, obj):
        time = obj.execution_time
        if time:
            return f"{time:.2f}s"
        return "-"
    execution_time_display.short_description = 'Time'


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'widget_type',
        'title',
        'color_preview',
        'width',
        'order',
        'is_active'
    ]
    list_filter = ['widget_type', 'is_active']
    search_fields = ['name', 'title']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Widget Info', {
            'fields': (('name', 'widget_type'), ('title', 'icon'))
        }),
        ('Data', {
            'fields': ('data_source', 'query_config')
        }),
        ('Display', {
            'fields': (('color', 'width'),)
        }),
        ('Status', {
            'fields': (('order', 'is_active'),)
        }),
    )
    
    def color_preview(self, obj):
        bootstrap_colors = {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
        }
        color = bootstrap_colors.get(obj.color, obj.color)
        return format_html(
            '<span style="background-color: {}; padding: 2px 10px; border-radius: 3px; color: white;">{}</span>',
            color, obj.color
        )
    color_preview.short_description = 'Color'
