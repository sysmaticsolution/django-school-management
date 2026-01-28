"""
Fee Management models for School Management System.
Handles fee structures, collections, and payment tracking.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.constants import FEE_TYPES


class FeeCategory(models.Model):
    """
    Categories of fees (Tuition, Transport, Hostel, etc.)
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Is this fee mandatory for all students?"
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_categories'
        verbose_name = 'Fee Category'
        verbose_name_plural = 'Fee Categories'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class FeeStructure(models.Model):
    """
    Fee structure for each class and academic year.
    Defines how much each fee type costs.
    """
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    standard = models.ForeignKey(
        'academics.Standard',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    fee_category = models.ForeignKey(
        FeeCategory,
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Payment frequency
    class Frequency(models.TextChoices):
        ONE_TIME = 'one_time', 'One Time'
        MONTHLY = 'monthly', 'Monthly'
        QUARTERLY = 'quarterly', 'Quarterly'
        HALF_YEARLY = 'half_yearly', 'Half Yearly'
        YEARLY = 'yearly', 'Yearly'
    
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.YEARLY
    )
    
    due_day = models.PositiveIntegerField(
        default=10,
        help_text="Day of month when fee is due"
    )
    late_fee_per_day = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Late fee charged per day after due date"
    )
    max_late_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Maximum late fee that can be charged"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_structures'
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
        unique_together = ['academic_year', 'standard', 'fee_category']
        ordering = ['academic_year', 'standard', 'fee_category']
    
    def __str__(self):
        return f"{self.academic_year} - {self.standard} - {self.fee_category}"


class FeeDiscount(models.Model):
    """
    Discount schemes (Sibling, RTE, Scholarship, etc.)
    """
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED = 'fixed', 'Fixed Amount'
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Percentage (0-100) or fixed amount"
    )
    applicable_categories = models.ManyToManyField(
        FeeCategory,
        related_name='discounts',
        blank=True,
        help_text="Leave empty to apply to all categories"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_discounts'
        verbose_name = 'Fee Discount'
        verbose_name_plural = 'Fee Discounts'
        ordering = ['name']
    
    def __str__(self):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return f"{self.name} ({self.value}%)"
        return f"{self.name} (₹{self.value})"


class StudentFee(models.Model):
    """
    Individual fee assignment to a student.
    Tracks what fees a student owes for an academic year.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='fees'
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name='student_fees'
    )
    
    # For periodic fees (monthly, quarterly, etc.)
    period_month = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Month number (1-12) for monthly fees"
    )
    period_quarter = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quarter number (1-4) for quarterly fees"
    )
    
    # Amounts
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.ForeignKey(
        FeeDiscount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_fees'
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    late_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Dates
    due_date = models.DateField()
    
    # Status
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PARTIAL = 'partial', 'Partially Paid'
        PAID = 'paid', 'Fully Paid'
        OVERDUE = 'overdue', 'Overdue'
        WAIVED = 'waived', 'Waived'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_fees'
        verbose_name = 'Student Fee'
        verbose_name_plural = 'Student Fees'
        ordering = ['-due_date', 'student']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.fee_structure.fee_category} - ₹{self.net_amount}"
    
    @property
    def balance_amount(self):
        """Amount remaining to be paid including late fee."""
        return self.net_amount + self.late_fee - self.paid_amount
    
    def save(self, *args, **kwargs):
        # Auto-update status based on payment
        if self.paid_amount >= (self.net_amount + self.late_fee):
            self.status = self.Status.PAID
        elif self.paid_amount > 0:
            self.status = self.Status.PARTIAL
        super().save(*args, **kwargs)


class FeePayment(models.Model):
    """
    Individual payment transactions against student fees.
    """
    class PaymentMode(models.TextChoices):
        CASH = 'cash', 'Cash'
        CHEQUE = 'cheque', 'Cheque'
        DD = 'dd', 'Demand Draft'
        ONLINE = 'online', 'Online Transfer'
        UPI = 'upi', 'UPI'
        CARD = 'card', 'Credit/Debit Card'
    
    # Receipt details
    receipt_number = models.CharField(max_length=30, unique=True)
    receipt_date = models.DateField()
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='fee_payments'
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_mode = models.CharField(
        max_length=20,
        choices=PaymentMode.choices,
        default=PaymentMode.CASH
    )
    
    # For cheque/DD payments
    cheque_number = models.CharField(max_length=20, blank=True)
    cheque_date = models.DateField(null=True, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    # For online payments
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Collected by
    collected_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='collected_payments'
    )
    
    remarks = models.TextField(blank=True)
    
    # Status
    class Status(models.TextChoices):
        SUCCESS = 'success', 'Success'
        PENDING = 'pending', 'Pending'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUCCESS
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_payments'
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'
        ordering = ['-receipt_date', '-created_at']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.student.full_name} - ₹{self.amount}"


class FeePaymentDetail(models.Model):
    """
    Links payments to specific student fees (for partial payments).
    """
    payment = models.ForeignKey(
        FeePayment,
        on_delete=models.CASCADE,
        related_name='details'
    )
    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='payment_details'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'fee_payment_details'
        verbose_name = 'Payment Detail'
        verbose_name_plural = 'Payment Details'
    
    def __str__(self):
        return f"{self.payment.receipt_number} - {self.student_fee.fee_structure.fee_category} - ₹{self.amount}"
