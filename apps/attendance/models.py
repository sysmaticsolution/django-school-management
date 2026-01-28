"""
Attendance Management models for School Management System.
Handles daily and subject-wise attendance for students and staff.
"""
from django.db import models
from apps.core.constants import ATTENDANCE_STATUS


class StudentAttendance(models.Model):
    """
    Daily attendance for students.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    section = models.ForeignKey(
        'academics.Section',
        on_delete=models.CASCADE,
        related_name='student_attendances'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='student_attendances'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='present'
    )
    remarks = models.CharField(max_length=200, blank=True)
    
    # Who marked the attendance
    marked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances'
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_attendances'
        verbose_name = 'Student Attendance'
        verbose_name_plural = 'Student Attendance'
        unique_together = ['student', 'date']
        ordering = ['-date', 'section', 'student']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.get_status_display()}"


class SubjectAttendance(models.Model):
    """
    Subject-wise attendance (for higher classes).
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='subject_attendances'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    section = models.ForeignKey(
        'academics.Section',
        on_delete=models.CASCADE,
        related_name='subject_attendances'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='subject_attendances'
    )
    date = models.DateField()
    period = models.PositiveIntegerField(
        help_text="Period/Session number (1-8)"
    )
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='present'
    )
    
    marked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_subject_attendances'
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subject_attendances'
        verbose_name = 'Subject Attendance'
        verbose_name_plural = 'Subject Attendance'
        unique_together = ['student', 'subject', 'date', 'period']
        ordering = ['-date', 'section', 'period']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.date}"


class AttendanceSummary(models.Model):
    """
    Monthly/Period-wise attendance summary for quick access.
    Auto-generated from daily attendance.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    section = models.ForeignKey(
        'academics.Section',
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='attendance_summaries'
    )
    month = models.PositiveIntegerField(help_text="Month (1-12)")
    year = models.PositiveIntegerField()
    
    # Counts
    total_working_days = models.PositiveIntegerField(default=0)
    present_days = models.PositiveIntegerField(default=0)
    absent_days = models.PositiveIntegerField(default=0)
    late_days = models.PositiveIntegerField(default=0)
    half_days = models.PositiveIntegerField(default=0)
    leave_days = models.PositiveIntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_summaries'
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'
        unique_together = ['student', 'month', 'year', 'academic_year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.month}/{self.year}"
    
    @property
    def attendance_percentage(self):
        if self.total_working_days == 0:
            return 0
        return round((self.present_days / self.total_working_days) * 100, 2)


class LeaveRequest(models.Model):
    """
    Leave applications from students/parents.
    """
    class LeaveType(models.TextChoices):
        SICK = 'sick', 'Sick Leave'
        CASUAL = 'casual', 'Casual Leave'
        EMERGENCY = 'emergency', 'Emergency'
        FUNCTION = 'function', 'Family Function'
        OTHER = 'other', 'Other'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices
    )
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    
    # Supporting document (medical certificate, etc.)
    attachment = models.FileField(
        upload_to='leave_attachments/',
        blank=True,
        null=True
    )
    
    # Applied by (can be parent)
    applied_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='leave_applications'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    
    # Approval
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leave_requests'
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_leave_type_display()} ({self.from_date} to {self.to_date})"
    
    @property
    def number_of_days(self):
        return (self.to_date - self.from_date).days + 1


class StaffAttendance(models.Model):
    """
    Daily attendance for teachers and staff.
    """
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        HALF_DAY = 'half_day', 'Half Day'
        ON_LEAVE = 'on_leave', 'On Leave'
        ON_DUTY = 'on_duty', 'On Duty'
    
    # Can be either teacher or staff
    teacher = models.ForeignKey(
        'staff.Teacher',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendances'
    )
    staff = models.ForeignKey(
        'staff.Staff',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attendances'
    )
    
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT
    )
    
    # Time tracking (optional)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    remarks = models.CharField(max_length=200, blank=True)
    
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_attendances'
        verbose_name = 'Staff Attendance'
        verbose_name_plural = 'Staff Attendance'
        ordering = ['-date']
    
    def __str__(self):
        staff_name = self.teacher.full_name if self.teacher else self.staff.full_name
        return f"{staff_name} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.teacher and not self.staff:
            raise ValidationError("Either teacher or staff must be selected.")
        if self.teacher and self.staff:
            raise ValidationError("Cannot select both teacher and staff.")
