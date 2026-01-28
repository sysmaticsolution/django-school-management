"""
Examination Management models for School Management System.
Handles exams, marks entry, grading, and results.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.constants import CBSE_GRADES


class ExamType(models.Model):
    """
    Types of exams (Unit Test, Quarterly, Half-Yearly, Annual, etc.)
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    weightage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        help_text="Weightage percentage for final result calculation"
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(
        default=1,
        help_text="Display order in reports"
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_types'
        verbose_name = 'Exam Type'
        verbose_name_plural = 'Exam Types'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Exam(models.Model):
    """
    Individual exam instance for a specific academic year.
    """
    name = models.CharField(max_length=200)
    exam_type = models.ForeignKey(
        ExamType,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='exams'
    )
    standards = models.ManyToManyField(
        'academics.Standard',
        related_name='exams',
        help_text="Classes for which this exam is being conducted"
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Status
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        ONGOING = 'ongoing', 'Ongoing'
        COMPLETED = 'completed', 'Completed'
        RESULTS_DECLARED = 'results_declared', 'Results Declared'
        CANCELLED = 'cancelled', 'Cancelled'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exams'
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.academic_year}"


class ExamSchedule(models.Model):
    """
    Timetable for exams - Subject-wise schedule.
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    standard = models.ForeignKey(
        'academics.Standard',
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    max_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=33)
    
    # Room assignment
    room_number = models.CharField(max_length=50, blank=True)
    
    # Invigilator
    invigilator = models.ForeignKey(
        'staff.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invigilated_exams'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_schedules'
        verbose_name = 'Exam Schedule'
        verbose_name_plural = 'Exam Schedules'
        unique_together = ['exam', 'standard', 'subject']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.exam.name} - {self.standard} - {self.subject}"


class ExamResult(models.Model):
    """
    Individual student marks for an exam subject.
    """
    exam_schedule = models.ForeignKey(
        ExamSchedule,
        on_delete=models.CASCADE,
        related_name='results'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_results'
    )
    
    # Marks
    theory_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    practical_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Total and Grade
    total_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    grade = models.CharField(
        max_length=10,
        choices=CBSE_GRADES,
        blank=True
    )
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ENTERED = 'entered', 'Entered'
        VERIFIED = 'verified', 'Verified'
        ABSENT = 'absent', 'Absent'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    is_passed = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)
    
    # Who entered the marks
    entered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_results'
    )
    entered_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_results'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_results'
        verbose_name = 'Exam Result'
        verbose_name_plural = 'Exam Results'
        unique_together = ['exam_schedule', 'student']
        ordering = ['exam_schedule', 'student']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.exam_schedule.subject} - {self.total_marks}"
    
    def save(self, *args, **kwargs):
        # Calculate total marks
        theory = self.theory_marks or Decimal('0')
        practical = self.practical_marks or Decimal('0')
        self.total_marks = theory + practical
        
        # Calculate percentage
        max_marks = self.exam_schedule.max_marks
        if max_marks > 0:
            self.percentage = (self.total_marks / Decimal(max_marks)) * 100
        
        # Determine pass/fail
        self.is_passed = self.total_marks >= self.exam_schedule.passing_marks
        
        # Auto-assign grade based on percentage
        if self.percentage:
            self.grade = self._calculate_grade(float(self.percentage))
        
        super().save(*args, **kwargs)
    
    def _calculate_grade(self, percentage):
        """CBSE grading system."""
        if percentage >= 91:
            return 'A1'
        elif percentage >= 81:
            return 'A2'
        elif percentage >= 71:
            return 'B1'
        elif percentage >= 61:
            return 'B2'
        elif percentage >= 51:
            return 'C1'
        elif percentage >= 41:
            return 'C2'
        elif percentage >= 33:
            return 'D'
        else:
            return 'E'


class ReportCard(models.Model):
    """
    Student report card for an exam (aggregated results).
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    section = models.ForeignKey(
        'academics.Section',
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    
    # Aggregated marks
    total_marks_obtained = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0')
    )
    total_max_marks = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0')
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0')
    )
    grade = models.CharField(max_length=10, blank=True)
    
    # Ranking
    rank_in_class = models.PositiveIntegerField(null=True, blank=True)
    rank_in_section = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        GENERATED = 'generated', 'Generated'
        PUBLISHED = 'published', 'Published'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Attendance for this period
    total_working_days = models.PositiveIntegerField(default=0)
    days_present = models.PositiveIntegerField(default=0)
    
    # Remarks
    class_teacher_remarks = models.TextField(blank=True)
    principal_remarks = models.TextField(blank=True)
    
    # Result
    is_promoted = models.BooleanField(null=True, blank=True)
    promoted_to = models.ForeignKey(
        'academics.Standard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promoted_students'
    )
    
    generated_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_cards'
        verbose_name = 'Report Card'
        verbose_name_plural = 'Report Cards'
        unique_together = ['student', 'exam']
        ordering = ['-exam__start_date', 'section', 'rank_in_section']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.exam.name}"
    
    @property
    def attendance_percentage(self):
        if self.total_working_days == 0:
            return 0
        return round((self.days_present / self.total_working_days) * 100, 2)
