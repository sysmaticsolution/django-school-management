"""
Core models for School Management System.
Contains school-wide configuration and settings.
"""
from django.db import models
from .constants import INDIAN_STATES, BOARD_TYPES


class SchoolProfile(models.Model):
    """
    School profile containing basic information and configuration.
    Only one active profile should exist at a time.
    """
    
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='school/', blank=True, null=True)
    
    # Contact Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=INDIAN_STATES)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Affiliation
    board_type = models.CharField(max_length=10, choices=BOARD_TYPES, default='cbse')
    affiliation_number = models.CharField(max_length=50, blank=True)
    udise_code = models.CharField(
        max_length=20, 
        blank=True,
        help_text="UDISE+ Code for government reporting"
    )
    
    # Principal
    principal_name = models.CharField(max_length=100)
    principal_signature = models.ImageField(upload_to='school/signatures/', blank=True, null=True)
    
    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_ifsc_code = models.CharField(max_length=11, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'school_profile'
        verbose_name = 'School Profile'
        verbose_name_plural = 'School Profile'
    
    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    """
    Academic year management (Indian system: April to March).
    """
    
    name = models.CharField(
        max_length=20,
        help_text="e.g., 2024-25"
    )
    start_date = models.DateField(help_text="Usually April 1st")
    end_date = models.DateField(help_text="Usually March 31st")
    is_current = models.BooleanField(
        default=False,
        help_text="Only one academic year should be current"
    )
    is_admission_open = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'academic_years'
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one academic year is current
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)
