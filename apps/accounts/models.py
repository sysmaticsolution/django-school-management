"""
Custom User model for School Management System.
Supports role-based access control for different user types.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Extends Django's AbstractUser with additional fields for Indian schools.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        PRINCIPAL = 'principal', 'Principal'
        TEACHER = 'teacher', 'Teacher'
        STAFF = 'staff', 'Staff'
        ACCOUNTANT = 'accountant', 'Accountant'
        LIBRARIAN = 'librarian', 'Librarian'
        PARENT = 'parent', 'Parent'
        STUDENT = 'student', 'Student'
    
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STAFF,
        help_text="User role determines access permissions"
    )
    phone = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Mobile number with country code"
    )
    aadhaar_number = models.CharField(
        max_length=12, 
        blank=True,
        help_text="12-digit Aadhaar number"
    )
    profile_picture = models.ImageField(
        upload_to='users/profiles/', 
        blank=True,
        null=True
    )
    address = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def is_principal(self):
        return self.role == self.Role.PRINCIPAL
    
    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
    
    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
    
    @property
    def is_student_user(self):
        return self.role == self.Role.STUDENT
