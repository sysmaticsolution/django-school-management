"""
Student models for School Management System.
Contains comprehensive student data with Indian-specific fields.
"""
from django.db import models
from apps.core.constants import GENDERS, BLOOD_GROUPS, CATEGORIES, RELIGIONS, INDIAN_STATES


class Student(models.Model):
    """
    Student master record with comprehensive Indian school requirements.
    """
    
    # Link to user account (optional)
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='student_profile'
    )
    
    # Basic Information
    admission_number = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Unique admission/registration number"
    )
    roll_number = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDERS)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    
    # Indian-specific fields
    aadhaar_number = models.CharField(
        max_length=12, 
        blank=True,
        help_text="12-digit Aadhaar number"
    )
    category = models.CharField(
        max_length=10, 
        choices=CATEGORIES, 
        default='general'
    )
    religion = models.CharField(max_length=20, choices=RELIGIONS, blank=True)
    caste = models.CharField(max_length=100, blank=True)
    sub_caste = models.CharField(max_length=100, blank=True)
    mother_tongue = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=50, default='Indian')
    
    # Contact Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, choices=INDIAN_STATES)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15, blank=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    # Father's Information
    father_name = models.CharField(max_length=100)
    father_phone = models.CharField(max_length=15, blank=True)
    father_email = models.EmailField(blank=True)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_qualification = models.CharField(max_length=100, blank=True)
    father_annual_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    father_aadhaar = models.CharField(max_length=12, blank=True)
    
    # Mother's Information
    mother_name = models.CharField(max_length=100)
    mother_phone = models.CharField(max_length=15, blank=True)
    mother_email = models.EmailField(blank=True)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_qualification = models.CharField(max_length=100, blank=True)
    mother_aadhaar = models.CharField(max_length=12, blank=True)
    
    # Guardian Information (if different from parents)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_address = models.TextField(blank=True)
    
    # Academic Information
    admission_date = models.DateField()
    current_section = models.ForeignKey(
        'academics.Section', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='students'
    )
    admission_class = models.ForeignKey(
        'academics.Standard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admitted_students',
        help_text="Class at the time of admission"
    )
    previous_school = models.CharField(max_length=200, blank=True)
    previous_class = models.CharField(max_length=50, blank=True)
    tc_number = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Transfer Certificate number from previous school"
    )
    
    # Health Information
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    # Status Flags
    is_active = models.BooleanField(default=True)
    is_rte = models.BooleanField(
        default=False,
        help_text="RTE (Right to Education) admission"
    )
    has_transport = models.BooleanField(default=False)
    has_hostel = models.BooleanField(default=False)
    has_scholarship = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['current_section', 'roll_number', 'first_name']
    
    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"
    
    @property
    def full_name(self):
        """Returns full name with middle name if present."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def class_and_section(self):
        """Returns class and section display name."""
        if self.current_section:
            return self.current_section.full_name
        return "Not Assigned"


class StudentDocument(models.Model):
    """
    Documents uploaded for a student (Birth Certificate, Aadhaar, TC, etc.)
    """
    
    class DocumentType(models.TextChoices):
        BIRTH_CERTIFICATE = 'birth_cert', 'Birth Certificate'
        AADHAAR_CARD = 'aadhaar', 'Aadhaar Card'
        TRANSFER_CERTIFICATE = 'tc', 'Transfer Certificate'
        CHARACTER_CERTIFICATE = 'cc', 'Character Certificate'
        CASTE_CERTIFICATE = 'caste', 'Caste Certificate'
        INCOME_CERTIFICATE = 'income', 'Income Certificate'
        MARKSHEET = 'marksheet', 'Previous Marksheet'
        PHOTO = 'photo', 'Passport Photo'
        OTHER = 'other', 'Other Document'
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='students/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_documents'
        verbose_name = 'Student Document'
        verbose_name_plural = 'Student Documents'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_document_type_display()}"
