"""
Reports and Analytics models for School Management System.
Handles saved reports, scheduled reports, and report templates.
"""
from django.db import models
from django.utils import timezone


class ReportCategory(models.Model):
    """
    Categories for organizing reports.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    icon = models.CharField(max_length=50, default='fas fa-chart-bar')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'report_categories'
        verbose_name = 'Report Category'
        verbose_name_plural = 'Report Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ReportTemplate(models.Model):
    """
    Predefined report templates.
    """
    class ReportType(models.TextChoices):
        STUDENT = 'student', 'Student Reports'
        ACADEMIC = 'academic', 'Academic Reports'
        FINANCIAL = 'financial', 'Financial Reports'
        ATTENDANCE = 'attendance', 'Attendance Reports'
        STAFF = 'staff', 'Staff Reports'
        INVENTORY = 'inventory', 'Inventory Reports'
        TRANSPORT = 'transport', 'Transport Reports'
        LIBRARY = 'library', 'Library Reports'
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    category = models.ForeignKey(
        ReportCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates'
    )
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices
    )
    
    # Query/filter configuration stored as JSON
    query_config = models.JSONField(
        default=dict,
        help_text="JSON configuration for report queries and filters"
    )
    
    # Available filters
    available_filters = models.JSONField(
        default=list,
        help_text="List of available filter fields"
    )
    
    # Output columns
    columns = models.JSONField(
        default=list,
        help_text="List of columns to display in report"
    )
    
    # Default export formats
    supports_pdf = models.BooleanField(default=True)
    supports_excel = models.BooleanField(default=True)
    supports_csv = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_templates'
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class SavedReport(models.Model):
    """
    User-saved reports with custom filters.
    """
    name = models.CharField(max_length=200)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='saved_reports'
    )
    
    # Saved filter values
    filter_values = models.JSONField(
        default=dict,
        help_text="Saved filter values for this report"
    )
    
    # Owner
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='saved_reports'
    )
    
    # Sharing
    is_shared = models.BooleanField(
        default=False,
        help_text="Make this report visible to others"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saved_reports'
        verbose_name = 'Saved Report'
        verbose_name_plural = 'Saved Reports'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.created_by.username})"


class ScheduledReport(models.Model):
    """
    Reports scheduled to run automatically.
    Uses Django 6.0 Background Tasks.
    """
    class Frequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'
        QUARTERLY = 'quarterly', 'Quarterly'
    
    class OutputFormat(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel'
        CSV = 'csv', 'CSV'
    
    name = models.CharField(max_length=200)
    saved_report = models.ForeignKey(
        SavedReport,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices
    )
    
    # Timing
    run_time = models.TimeField(help_text="Time of day to run")
    day_of_week = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="For weekly: 1=Monday, 7=Sunday"
    )
    day_of_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="For monthly/quarterly"
    )
    
    output_format = models.CharField(
        max_length=10,
        choices=OutputFormat.choices,
        default=OutputFormat.PDF
    )
    
    # Email recipients
    email_recipients = models.TextField(
        help_text="Comma-separated email addresses"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='scheduled_reports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_reports'
        verbose_name = 'Scheduled Report'
        verbose_name_plural = 'Scheduled Reports'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class ReportExecution(models.Model):
    """
    Log of report executions.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    saved_report = models.ForeignKey(
        SavedReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions'
    )
    scheduled_report = models.ForeignKey(
        ScheduledReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions'
    )
    
    # Parameters used
    parameters = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Output
    output_file = models.FileField(
        upload_to='reports/output/',
        blank=True,
        null=True
    )
    row_count = models.PositiveIntegerField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    
    executed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='report_executions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_executions'
        verbose_name = 'Report Execution'
        verbose_name_plural = 'Report Executions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def execution_time(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class DashboardWidget(models.Model):
    """
    Configurable dashboard widgets for analytics.
    """
    class WidgetType(models.TextChoices):
        NUMBER = 'number', 'Single Number'
        CHART_LINE = 'chart_line', 'Line Chart'
        CHART_BAR = 'chart_bar', 'Bar Chart'
        CHART_PIE = 'chart_pie', 'Pie Chart'
        TABLE = 'table', 'Data Table'
        LIST = 'list', 'List'
    
    name = models.CharField(max_length=100)
    widget_type = models.CharField(
        max_length=20,
        choices=WidgetType.choices
    )
    
    # Data configuration
    data_source = models.CharField(
        max_length=100,
        help_text="Model or custom function name"
    )
    query_config = models.JSONField(default=dict)
    
    # Display settings
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, default='primary')
    
    # Size
    width = models.PositiveIntegerField(
        default=3,
        help_text="Width in grid columns (1-12)"
    )
    
    order = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widgets'
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"
