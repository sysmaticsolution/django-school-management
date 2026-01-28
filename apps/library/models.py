"""
Library Management models for School Management System.
Handles books, issues, returns, and fines.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import date, timedelta


class BookCategory(models.Model):
    """
    Categories for organizing books.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'book_categories'
        verbose_name = 'Book Category'
        verbose_name_plural = 'Book Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BookRack(models.Model):
    """
    Physical location of books in library.
    """
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'book_racks'
        verbose_name = 'Book Rack'
        verbose_name_plural = 'Book Racks'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Book(models.Model):
    """
    Book master data.
    """
    # Book details
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=20, blank=True, help_text="ISBN-10 or ISBN-13")
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    
    # Classification
    category = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    rack = models.ForeignKey(
        BookRack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    
    # Physical details
    pages = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='English')
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Stock
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    
    # Book cover
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)
    
    # Description
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class LibraryMember(models.Model):
    """
    Library membership for students and staff.
    """
    class MemberType(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        STAFF = 'staff', 'Staff'
    
    # Link to user
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='library_member'
    )
    
    member_type = models.CharField(
        max_length=20,
        choices=MemberType.choices
    )
    membership_number = models.CharField(max_length=30, unique=True)
    
    # Limits
    max_books_allowed = models.PositiveIntegerField(default=3)
    max_days_allowed = models.PositiveIntegerField(default=14)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'library_members'
        verbose_name = 'Library Member'
        verbose_name_plural = 'Library Members'
        ordering = ['membership_number']
    
    def __str__(self):
        return f"{self.membership_number} - {self.user.get_full_name()}"
    
    @property
    def books_issued_count(self):
        return self.issues.filter(status='issued').count()
    
    @property
    def can_issue_book(self):
        return self.books_issued_count < self.max_books_allowed


class BookIssue(models.Model):
    """
    Book issue/return tracking.
    """
    class Status(models.TextChoices):
        ISSUED = 'issued', 'Issued'
        RETURNED = 'returned', 'Returned'
        LOST = 'lost', 'Lost'
        DAMAGED = 'damaged', 'Damaged'
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    member = models.ForeignKey(
        LibraryMember,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    
    # Issue details
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ISSUED
    )
    
    # Fine
    fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    fine_paid = models.BooleanField(default=False)
    
    remarks = models.TextField(blank=True)
    
    # Issued/returned by
    issued_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='books_issued'
    )
    returned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books_returned'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'book_issues'
        verbose_name = 'Book Issue'
        verbose_name_plural = 'Book Issues'
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.book.title} → {self.member.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Set default due date if not provided
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=self.member.max_days_allowed)
        
        # Update book availability
        if self.pk is None:  # New issue
            self.book.available_copies -= 1
            self.book.save()
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.status == self.Status.ISSUED:
            return date.today() > self.due_date
        return False
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0


class LibrarySetting(models.Model):
    """
    Library configuration settings.
    """
    fine_per_day = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Fine amount per day for overdue books"
    )
    max_fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('100.00'),
        help_text="Maximum fine that can be charged"
    )
    lost_book_penalty_percentage = models.PositiveIntegerField(
        default=150,
        help_text="Penalty for lost book as % of book price"
    )
    damaged_book_penalty_percentage = models.PositiveIntegerField(
        default=75,
        help_text="Penalty for damaged book as % of book price"
    )
    
    class Meta:
        db_table = 'library_settings'
        verbose_name = 'Library Setting'
        verbose_name_plural = 'Library Settings'
    
    def __str__(self):
        return "Library Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
