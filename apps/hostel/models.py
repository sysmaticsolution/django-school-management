"""
Hostel Management models for School Management System.
Handles hostels, rooms, bed allocation, and mess management.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Hostel(models.Model):
    """
    Hostel buildings.
    """
    class HostelType(models.TextChoices):
        BOYS = 'boys', 'Boys Hostel'
        GIRLS = 'girls', 'Girls Hostel'
        STAFF = 'staff', 'Staff Quarters'
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    hostel_type = models.CharField(
        max_length=20,
        choices=HostelType.choices
    )
    
    # Location
    address = models.TextField(blank=True)
    
    # Capacity
    total_rooms = models.PositiveIntegerField(default=0)
    total_beds = models.PositiveIntegerField(default=0)
    
    # Warden
    warden = models.ForeignKey(
        'staff.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hostels_in_charge'
    )
    
    # Contact
    phone = models.CharField(max_length=15, blank=True)
    
    # Fees
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hostels'
        verbose_name = 'Hostel'
        verbose_name_plural = 'Hostels'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_hostel_type_display()})"
    
    @property
    def occupied_beds(self):
        return self.rooms.aggregate(
            total=models.Sum('current_occupancy')
        )['total'] or 0
    
    @property
    def available_beds(self):
        return self.total_beds - self.occupied_beds


class HostelRoom(models.Model):
    """
    Individual rooms in a hostel.
    """
    class RoomType(models.TextChoices):
        SINGLE = 'single', 'Single (1 bed)'
        DOUBLE = 'double', 'Double (2 beds)'
        TRIPLE = 'triple', 'Triple (3 beds)'
        DORMITORY = 'dormitory', 'Dormitory (4+ beds)'
    
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    
    room_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField(default=0)
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.DOUBLE
    )
    
    # Capacity
    bed_count = models.PositiveIntegerField(default=2)
    current_occupancy = models.PositiveIntegerField(default=0)
    
    # Amenities
    has_attached_bathroom = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_wardrobe = models.BooleanField(default=True)
    has_study_table = models.BooleanField(default=True)
    
    # Additional fee for special rooms
    additional_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    remarks = models.TextField(blank=True)
    
    is_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'hostel_rooms'
        verbose_name = 'Hostel Room'
        verbose_name_plural = 'Hostel Rooms'
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'floor', 'room_number']
    
    def __str__(self):
        return f"{self.hostel.code} - Room {self.room_number}"
    
    @property
    def is_full(self):
        return self.current_occupancy >= self.bed_count
    
    @property
    def available_beds(self):
        return self.bed_count - self.current_occupancy


class HostelAllocation(models.Model):
    """
    Student hostel room allocation.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='hostel_allocations'
    )
    room = models.ForeignKey(
        HostelRoom,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='hostel_allocations'
    )
    
    bed_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Duration
    allocation_date = models.DateField()
    vacating_date = models.DateField(null=True, blank=True)
    
    # Monthly fee for this student
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hostel_allocations'
        verbose_name = 'Hostel Allocation'
        verbose_name_plural = 'Hostel Allocations'
        ordering = ['-allocation_date']
    
    def __str__(self):
        return f"{self.student.full_name} → {self.room}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New allocation
            self.room.current_occupancy += 1
            self.room.save()
        super().save(*args, **kwargs)


class MessMenu(models.Model):
    """
    Weekly mess menu.
    """
    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast', 'Breakfast'
        LUNCH = 'lunch', 'Lunch'
        SNACKS = 'snacks', 'Evening Snacks'
        DINNER = 'dinner', 'Dinner'
    
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'
        SUNDAY = 7, 'Sunday'
    
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name='mess_menus'
    )
    
    day = models.PositiveIntegerField(choices=DayOfWeek.choices)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    menu_items = models.TextField(help_text="List of items for this meal")
    
    timing = models.CharField(max_length=50, blank=True, help_text="e.g., 7:30 AM - 9:00 AM")
    
    class Meta:
        db_table = 'mess_menus'
        verbose_name = 'Mess Menu'
        verbose_name_plural = 'Mess Menus'
        unique_together = ['hostel', 'day', 'meal_type']
        ordering = ['hostel', 'day', 'meal_type']
    
    def __str__(self):
        return f"{self.hostel.code} - {self.get_day_display()} - {self.get_meal_type_display()}"


class HostelVisitor(models.Model):
    """
    Visitor log for hostel students.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='hostel_visitors'
    )
    
    # Visitor details
    visitor_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    id_proof_type = models.CharField(max_length=50, blank=True)
    id_proof_number = models.CharField(max_length=50, blank=True)
    
    # Visit timing
    visit_date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    
    purpose = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)
    
    # Approved by
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_hostel_visits'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hostel_visitors'
        verbose_name = 'Hostel Visitor'
        verbose_name_plural = 'Hostel Visitors'
        ordering = ['-visit_date', '-check_in_time']
    
    def __str__(self):
        return f"{self.visitor_name} → {self.student.full_name} ({self.visit_date})"


class LeavePass(models.Model):
    """
    Leave/outing pass for hostel students.
    """
    class LeaveType(models.TextChoices):
        DAY_OUTING = 'day_outing', 'Day Outing'
        OVERNIGHT = 'overnight', 'Overnight Leave'
        WEEKEND = 'weekend', 'Weekend Leave'
        HOLIDAY = 'holiday', 'Holiday Leave'
        EMERGENCY = 'emergency', 'Emergency Leave'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        RETURNED = 'returned', 'Returned'
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='leave_passes'
    )
    
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    
    # Duration
    from_date = models.DateField()
    from_time = models.TimeField()
    to_date = models.DateField()
    to_time = models.TimeField()
    
    # Destination
    destination = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=15)
    
    reason = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Actual return
    actual_return_date = models.DateField(null=True, blank=True)
    actual_return_time = models.TimeField(null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_passes'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hostel_leave_passes'
        verbose_name = 'Leave Pass'
        verbose_name_plural = 'Leave Passes'
        ordering = ['-from_date', '-created_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.get_leave_type_display()} ({self.from_date})"
