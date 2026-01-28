"""
Communication models for School Management System.
Handles notices, announcements, SMS, emails, and in-app messaging.
Uses Django 6.0 Background Tasks for async sending.
"""
from django.db import models
from django.utils import timezone


class Notice(models.Model):
    """
    School notices and announcements.
    """
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        NORMAL = 'normal', 'Normal'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    class Audience(models.TextChoices):
        ALL = 'all', 'All'
        STUDENTS = 'students', 'Students Only'
        PARENTS = 'parents', 'Parents Only'
        TEACHERS = 'teachers', 'Teachers Only'
        STAFF = 'staff', 'Staff Only'
        SPECIFIC_CLASS = 'specific_class', 'Specific Class'
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Targeting
    audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.ALL
    )
    target_classes = models.ManyToManyField(
        'academics.Standard',
        blank=True,
        related_name='notices',
        help_text="Select classes if audience is 'Specific Class'"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    
    # Attachments
    attachment = models.FileField(
        upload_to='notices/',
        blank=True,
        null=True
    )
    
    # Publishing
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Author
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_notices'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notices'
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def publish(self):
        """Publish the notice."""
        self.is_published = True
        self.publish_date = timezone.now()
        self.save()


class SMSLog(models.Model):
    """
    Log of SMS messages sent.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        DELIVERED = 'delivered', 'Delivered'
        FAILED = 'failed', 'Failed'
    
    # Recipient info
    phone_number = models.CharField(max_length=15)
    
    # Linked entities (optional)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_logs'
    )
    
    message = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Gateway response
    message_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Sent by
    sent_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_sms'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_logs'
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} - {self.message[:30]}..."


class EmailLog(models.Model):
    """
    Log of emails sent.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
    
    # Recipient
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=100, blank=True)
    
    # Linked entities (optional)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_html = models.BooleanField(default=False)
    
    # Attachment
    attachment = models.FileField(
        upload_to='email_attachments/',
        blank=True,
        null=True
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Sent by
    sent_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_emails'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_email} - {self.subject}"


class MessageTemplate(models.Model):
    """
    Reusable message templates for SMS/Email.
    """
    class TemplateType(models.TextChoices):
        SMS = 'sms', 'SMS'
        EMAIL = 'email', 'Email'
        BOTH = 'both', 'Both'
    
    class Category(models.TextChoices):
        FEE_REMINDER = 'fee_reminder', 'Fee Reminder'
        ATTENDANCE = 'attendance', 'Attendance Alert'
        EXAM = 'exam', 'Exam Related'
        HOLIDAY = 'holiday', 'Holiday Notice'
        EVENT = 'event', 'Event Invitation'
        GENERAL = 'general', 'General'
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )
    
    # Template content with placeholders
    subject = models.CharField(
        max_length=200,
        blank=True,
        help_text="For email templates"
    )
    body = models.TextField(
        help_text="Use {student_name}, {class}, {amount}, {date} as placeholders"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'message_templates'
        verbose_name = 'Message Template'
        verbose_name_plural = 'Message Templates'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def render(self, context: dict) -> str:
        """Render template with context variables."""
        text = self.body
        for key, value in context.items():
            text = text.replace(f'{{{key}}}', str(value))
        return text


class Notification(models.Model):
    """
    In-app notifications for users.
    """
    class NotificationType(models.TextChoices):
        INFO = 'info', 'Information'
        SUCCESS = 'success', 'Success'
        WARNING = 'warning', 'Warning'
        ERROR = 'error', 'Error'
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    
    # Link to related page
    url = models.CharField(max_length=500, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Event(models.Model):
    """
    School events and calendar.
    """
    class EventType(models.TextChoices):
        HOLIDAY = 'holiday', 'Holiday'
        EXAM = 'exam', 'Examination'
        MEETING = 'meeting', 'Meeting'
        FUNCTION = 'function', 'Function/Celebration'
        SPORTS = 'sports', 'Sports Event'
        CULTURAL = 'cultural', 'Cultural Event'
        PTM = 'ptm', 'Parent-Teacher Meeting'
        OTHER = 'other', 'Other'
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER
    )
    
    # Date and time
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # All day event
    is_all_day = models.BooleanField(default=True)
    
    # Location
    venue = models.CharField(max_length=200, blank=True)
    
    # For whom
    audience = models.CharField(
        max_length=20,
        choices=Notice.Audience.choices,
        default=Notice.Audience.ALL
    )
    
    # Color for calendar display
    color = models.CharField(
        max_length=20,
        default='#3788d8',
        help_text="Hex color code for calendar display"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['start_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} ({self.start_date})"
