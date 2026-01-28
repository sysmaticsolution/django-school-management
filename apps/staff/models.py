"""
Staff models for School Management System.
Manages teachers, staff members, departments, and designations.
"""
from django.db import models
from apps.core.constants import GENDERS, BLOOD_GROUPS, INDIAN_STATES, CATEGORIES, RELIGIONS


class Department(models.Model):
    """
    School departments (e.g., Science, Arts, Administration).
    """
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        'Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='headed_department'
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Designation(models.Model):
    """
    Staff designations/positions (e.g., Principal, PGT, TGT, Clerk).
    """
    
    class StaffCategory(models.TextChoices):
        TEACHING = 'teaching', 'Teaching Staff'
        NON_TEACHING = 'non_teaching', 'Non-Teaching Staff'
        ADMINISTRATION = 'admin', 'Administration'
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20, 
        choices=StaffCategory.choices,
        default=StaffCategory.TEACHING
    )
    pay_grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'designations'
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Teacher(models.Model):
    """
    Teacher/Teaching staff model.
    """
    
    # Link to user account
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='teacher_profile'
    )
    
    # Basic Information
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDERS)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    photo = models.ImageField(upload_to='staff/photos/', blank=True, null=True)
    
    # Indian-specific
    aadhaar_number = models.CharField(max_length=12, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORIES, default='general')
    religion = models.CharField(max_length=20, choices=RELIGIONS, blank=True)
    
    # Contact
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=INDIAN_STATES)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    emergency_contact = models.CharField(max_length=15, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    
    # Professional Information
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='teachers'
    )
    designation = models.ForeignKey(
        Designation, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='teachers'
    )
    subjects = models.ManyToManyField(
        'academics.Subject',
        related_name='teachers',
        blank=True
    )
    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    
    # Employment Details
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('permanent', 'Permanent'),
            ('contractual', 'Contractual'),
            ('part_time', 'Part Time'),
            ('guest', 'Guest Faculty'),
        ],
        default='permanent'
    )
    
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
        db_table = 'teachers'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Staff(models.Model):
    """
    Non-teaching staff model (Office staff, Peons, Guards, etc.)
    """
    
    # Link to user account
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='staff_profile'
    )
    
    # Basic Information
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDERS)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    photo = models.ImageField(upload_to='staff/photos/', blank=True, null=True)
    
    # Indian-specific
    aadhaar_number = models.CharField(max_length=12, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    
    # Contact
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=INDIAN_STATES)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    
    # Professional Information
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='staff_members'
    )
    designation = models.ForeignKey(
        Designation, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='staff_members'
    )
    
    # Employment Details
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=[
            ('permanent', 'Permanent'),
            ('contractual', 'Contractual'),
            ('part_time', 'Part Time'),
        ],
        default='permanent'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'staff_members'
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
