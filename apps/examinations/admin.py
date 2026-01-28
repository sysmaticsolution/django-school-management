"""
Admin configuration for examinations app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ExamType, Exam, ExamSchedule, ExamResult, ReportCard


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'weightage', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    list_editable = ['order', 'is_active']


class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 1
    autocomplete_fields = ['standard', 'subject', 'invigilator']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'start_date', 'end_date', 'status_colored']
    list_filter = ['status', 'exam_type', 'academic_year', 'start_date']
    search_fields = ['name']
    date_hierarchy = 'start_date'
    filter_horizontal = ['standards']
    autocomplete_fields = ['exam_type', 'academic_year']
    inlines = [ExamScheduleInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'exam_type', 'academic_year')
        }),
        ('Schedule', {
            'fields': (('start_date', 'end_date'), 'standards')
        }),
        ('Status', {
            'fields': ('status', 'remarks')
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'scheduled': 'blue',
            'ongoing': 'orange',
            'completed': 'purple',
            'results_declared': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['exam', 'standard', 'subject', 'date', 'time_display', 'max_marks', 'room_number']
    list_filter = ['exam', 'standard', 'subject', 'date']
    search_fields = ['exam__name', 'subject__name']
    date_hierarchy = 'date'
    autocomplete_fields = ['exam', 'standard', 'subject', 'invigilator']
    
    fieldsets = (
        ('Exam & Subject', {
            'fields': ('exam', 'standard', 'subject')
        }),
        ('Schedule', {
            'fields': ('date', ('start_time', 'end_time'))
        }),
        ('Marks', {
            'fields': (('max_marks', 'passing_marks'),)
        }),
        ('Venue', {
            'fields': ('room_number', 'invigilator')
        }),
    )
    
    def time_display(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_display.short_description = 'Time'


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'subject_display',
        'theory_marks',
        'practical_marks',
        'total_marks',
        'percentage_display',
        'grade_colored',
        'status',
        'result_display'
    ]
    list_filter = [
        'status',
        'is_passed',
        'grade',
        'exam_schedule__exam',
        'exam_schedule__standard',
        'exam_schedule__subject'
    ]
    search_fields = [
        'student__first_name',
        'student__last_name',
        'student__admission_number'
    ]
    autocomplete_fields = ['exam_schedule', 'student']
    readonly_fields = ['total_marks', 'percentage', 'grade', 'is_passed']
    list_per_page = 50
    
    fieldsets = (
        ('Exam & Student', {
            'fields': ('exam_schedule', 'student')
        }),
        ('Marks Entry', {
            'fields': (('theory_marks', 'practical_marks'),)
        }),
        ('Calculated Results', {
            'fields': (('total_marks', 'percentage'), ('grade', 'is_passed')),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'remarks')
        }),
    )
    
    def subject_display(self, obj):
        return obj.exam_schedule.subject.name
    subject_display.short_description = 'Subject'
    
    def percentage_display(self, obj):
        if obj.percentage:
            return f"{obj.percentage:.1f}%"
        return "-"
    percentage_display.short_description = '%'
    
    def grade_colored(self, obj):
        colors = {
            'A1': 'darkgreen', 'A2': 'green',
            'B1': 'blue', 'B2': 'dodgerblue',
            'C1': 'orange', 'C2': 'darkorange',
            'D': 'brown', 'E': 'red',
        }
        color = colors.get(obj.grade, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.grade or '-'
        )
    grade_colored.short_description = 'Grade'
    
    def result_display(self, obj):
        if obj.is_passed:
            return format_html('<span style="color: green;">✓ Pass</span>')
        elif obj.status == 'absent':
            return format_html('<span style="color: gray;">Absent</span>')
        else:
            return format_html('<span style="color: red;">✗ Fail</span>')
    result_display.short_description = 'Result'


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'exam',
        'section',
        'total_marks_obtained',
        'percentage_display',
        'grade',
        'rank_in_section',
        'rank_in_class',
        'status_colored',
        'promoted_display'
    ]
    list_filter = ['status', 'exam', 'section__standard', 'section', 'is_promoted']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
    autocomplete_fields = ['student', 'exam', 'section', 'promoted_to']
    readonly_fields = ['generated_at', 'published_at']
    
    fieldsets = (
        ('Student & Exam', {
            'fields': ('student', 'exam', 'section')
        }),
        ('Results', {
            'fields': (
                ('total_marks_obtained', 'total_max_marks'),
                ('percentage', 'grade'),
                ('rank_in_section', 'rank_in_class')
            )
        }),
        ('Attendance', {
            'fields': (('total_working_days', 'days_present'),)
        }),
        ('Remarks', {
            'fields': ('class_teacher_remarks', 'principal_remarks')
        }),
        ('Promotion', {
            'fields': ('is_promoted', 'promoted_to')
        }),
        ('Status', {
            'fields': ('status', 'generated_at', 'published_at')
        }),
    )
    
    def percentage_display(self, obj):
        return f"{obj.percentage:.1f}%"
    percentage_display.short_description = '%'
    
    def status_colored(self, obj):
        colors = {
            'draft': 'gray',
            'generated': 'blue',
            'published': 'green',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def promoted_display(self, obj):
        if obj.is_promoted is True:
            return format_html('<span style="color: green;">✓ Promoted</span>')
        elif obj.is_promoted is False:
            return format_html('<span style="color: red;">✗ Detained</span>')
        return "-"
    promoted_display.short_description = 'Promotion'
