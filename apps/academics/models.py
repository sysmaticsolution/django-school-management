"""
Academic models for School Management System.
Manages classes, sections, and subjects.
"""
from django.db import models


class Standard(models.Model):
    """
    School class/standard (e.g., Class 1 to Class 12).
    Also known as Grade in some systems.
    """
    
    name = models.CharField(
        max_length=50,
        help_text="e.g., Class 1, Class 10, KG"
    )
    numeric_value = models.PositiveIntegerField(
        help_text="Numeric order for sorting (0 for KG, 1-12 for classes)"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'standards'
        verbose_name = 'Class/Standard'
        verbose_name_plural = 'Classes/Standards'
        ordering = ['numeric_value']
    
    def __str__(self):
        return self.name


class Section(models.Model):
    """
    Sections within a class (e.g., 10-A, 10-B, 10-C).
    """
    
    standard = models.ForeignKey(
        Standard, 
        on_delete=models.CASCADE, 
        related_name='sections'
    )
    name = models.CharField(
        max_length=10,
        help_text="e.g., A, B, C"
    )
    class_teacher = models.ForeignKey(
        'staff.Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='class_sections'
    )
    room_number = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(
        default=40,
        help_text="Maximum students allowed"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        unique_together = ['standard', 'name']
        ordering = ['standard__numeric_value', 'name']
    
    def __str__(self):
        return f"{self.standard.name} - {self.name}"
    
    @property
    def full_name(self):
        return f"{self.standard.name} ({self.name})"


class Subject(models.Model):
    """
    Subjects taught in the school.
    """
    
    class SubjectType(models.TextChoices):
        THEORY = 'theory', 'Theory'
        PRACTICAL = 'practical', 'Practical'
        BOTH = 'both', 'Theory + Practical'
    
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Subject code e.g., MATH101"
    )
    subject_type = models.CharField(
        max_length=10, 
        choices=SubjectType.choices, 
        default=SubjectType.THEORY
    )
    description = models.TextField(blank=True)
    
    # Marks configuration
    max_theory_marks = models.PositiveIntegerField(default=100)
    max_practical_marks = models.PositiveIntegerField(default=0)
    passing_percentage = models.PositiveIntegerField(default=33)
    
    # Class assignment
    standards = models.ManyToManyField(
        Standard, 
        related_name='subjects',
        blank=True,
        help_text="Classes where this subject is taught"
    )
    
    is_optional = models.BooleanField(
        default=False,
        help_text="Is this an optional/elective subject?"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def total_marks(self):
        return self.max_theory_marks + self.max_practical_marks
