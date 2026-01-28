"""
Admin configuration for attendance app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import StudentAttendance, SubjectAttendance, AttendanceSummary, LeaveRequest, StaffAttendance


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'section', 'date', 'status_colored', 'marked_by']
    list_filter = ['status', 'section__standard', 'section', 'date', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
    date_hierarchy = 'date'
    autocomplete_fields = ['student', 'section', 'academic_year']
    list_per_page = 50
    
    fieldsets = (
        ('Student Info', {
            'fields': ('student', 'section', 'academic_year')
        }),
        ('Attendance', {
            'fields': ('date', 'status', 'remarks')
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'half_day': 'blue',
            'leave': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(SubjectAttendance)
class SubjectAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'section', 'date', 'period', 'status']
    list_filter = ['status', 'subject', 'section', 'date']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'date'
    autocomplete_fields = ['student', 'subject', 'section', 'academic_year']


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'student', 
        'section',
        'month_year',
        'total_working_days',
        'present_days',
        'absent_days',
        'attendance_percentage_display'
    ]
    list_filter = ['section__standard', 'section', 'month', 'year', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name']
    readonly_fields = ['attendance_percentage']
    
    def month_year(self, obj):
        months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{months[obj.month]} {obj.year}"
    month_year.short_description = 'Period'
    
    def attendance_percentage_display(self, obj):
        pct = obj.attendance_percentage
        if pct >= 75:
            color = 'green'
        elif pct >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, pct
        )
    attendance_percentage_display.short_description = 'Attendance %'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'leave_type',
        'from_date',
        'to_date',
        'number_of_days',
        'status_colored',
        'applied_at'
    ]
    list_filter = ['status', 'leave_type', 'from_date']
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    date_hierarchy = 'from_date'
    autocomplete_fields = ['student']
    readonly_fields = ['applied_at', 'applied_by', 'approved_at']
    
    fieldsets = (
        ('Student & Leave Type', {
            'fields': ('student', 'leave_type')
        }),
        ('Duration', {
            'fields': (('from_date', 'to_date'), 'reason', 'attachment')
        }),
        ('Application Info', {
            'fields': ('applied_by', 'applied_at'),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'approval_remarks')
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff_name', 'date', 'status_colored', 'check_in_time', 'check_out_time']
    list_filter = ['status', 'date']
    search_fields = [
        'teacher__first_name', 'teacher__last_name',
        'staff__first_name', 'staff__last_name'
    ]
    date_hierarchy = 'date'
    autocomplete_fields = ['teacher', 'staff']
    
    fieldsets = (
        ('Staff Member', {
            'fields': ('teacher', 'staff'),
            'description': 'Select either teacher or staff member'
        }),
        ('Attendance', {
            'fields': ('date', 'status', ('check_in_time', 'check_out_time'), 'remarks')
        }),
    )
    
    def staff_name(self, obj):
        return obj.teacher.full_name if obj.teacher else obj.staff.full_name
    staff_name.short_description = 'Staff Member'
    
    def status_colored(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'half_day': 'orange',
            'on_leave': 'blue',
            'on_duty': 'purple',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
