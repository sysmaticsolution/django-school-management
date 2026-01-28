"""
Admin configuration for communication app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Notice, SMSLog, EmailLog, MessageTemplate, Notification, Event


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'audience',
        'priority_colored',
        'is_published',
        'publish_date',
        'expiry_date',
        'created_by'
    ]
    list_filter = ['is_published', 'priority', 'audience', 'publish_date']
    search_fields = ['title', 'content']
    filter_horizontal = ['target_classes']
    date_hierarchy = 'publish_date'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'attachment')
        }),
        ('Targeting', {
            'fields': ('audience', 'target_classes', 'priority')
        }),
        ('Publishing', {
            'fields': ('is_published', ('publish_date', 'expiry_date'))
        }),
    )
    
    actions = ['publish_selected']
    
    def priority_colored(self, obj):
        colors = {
            'low': 'gray',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red',
        }
        color = colors.get(obj.priority, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_colored.short_description = 'Priority'
    
    def publish_selected(self, request, queryset):
        count = queryset.update(is_published=True, publish_date=timezone.now())
        self.message_user(request, f"{count} notice(s) published.")
    publish_selected.short_description = "Publish selected notices"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = [
        'phone_number',
        'student',
        'message_preview',
        'status_colored',
        'sent_at',
        'sent_by'
    ]
    list_filter = ['status', 'sent_at']
    search_fields = ['phone_number', 'message', 'student__first_name', 'student__last_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['message_id', 'error_message', 'sent_at', 'delivered_at', 'created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def status_colored(self, obj):
        colors = {
            'pending': 'gray',
            'sent': 'blue',
            'delivered': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = [
        'recipient_email',
        'subject',
        'status_colored',
        'sent_at',
        'sent_by'
    ]
    list_filter = ['status', 'sent_at', 'is_html']
    search_fields = ['recipient_email', 'subject', 'body']
    date_hierarchy = 'created_at'
    readonly_fields = ['error_message', 'sent_at', 'created_at']
    
    def status_colored(self, obj):
        colors = {
            'pending': 'gray',
            'sent': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'template_type', 'category', 'is_active']
    list_filter = ['template_type', 'category', 'is_active']
    search_fields = ['name', 'code', 'body']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Template Info', {
            'fields': (('name', 'code'), ('template_type', 'category'))
        }),
        ('Content', {
            'fields': ('subject', 'body'),
            'description': 'Use placeholders: {student_name}, {class}, {amount}, {date}, {school_name}'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'title',
        'notification_type_colored',
        'is_read',
        'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    date_hierarchy = 'created_at'
    
    def notification_type_colored(self, obj):
        colors = {
            'info': 'blue',
            'success': 'green',
            'warning': 'orange',
            'error': 'red',
        }
        color = colors.get(obj.notification_type, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_notification_type_display()
        )
    notification_type_colored.short_description = 'Type'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'event_type',
        'date_display',
        'venue',
        'audience',
        'color_preview',
        'is_active'
    ]
    list_filter = ['event_type', 'audience', 'is_active', 'start_date']
    search_fields = ['title', 'description', 'venue']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'event_type')
        }),
        ('Date & Time', {
            'fields': (
                ('start_date', 'end_date'),
                ('start_time', 'end_time'),
                'is_all_day'
            )
        }),
        ('Location & Audience', {
            'fields': ('venue', 'audience')
        }),
        ('Display', {
            'fields': ('color', 'is_active')
        }),
    )
    
    def date_display(self, obj):
        if obj.start_date == obj.end_date:
            return obj.start_date.strftime('%d %b %Y')
        return f"{obj.start_date.strftime('%d %b')} - {obj.end_date.strftime('%d %b %Y')}"
    date_display.short_description = 'Date'
    
    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 2px 10px; border-radius: 3px;">&nbsp;</span>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
