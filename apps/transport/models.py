"""
Transport Management models for School Management System.
Handles routes, vehicles, drivers, and student transport assignments.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Vehicle(models.Model):
    """
    School vehicles (buses, vans, etc.)
    """
    class VehicleType(models.TextChoices):
        BUS = 'bus', 'Bus'
        MINI_BUS = 'mini_bus', 'Mini Bus'
        VAN = 'van', 'Van'
        AUTO = 'auto', 'Auto Rickshaw'
    
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.BUS
    )
    make = models.CharField(max_length=50, help_text="Vehicle manufacturer")
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    seating_capacity = models.PositiveIntegerField()
    
    # Documents
    registration_number = models.CharField(max_length=50)
    insurance_number = models.CharField(max_length=50)
    insurance_expiry = models.DateField()
    fitness_expiry = models.DateField()
    pollution_expiry = models.DateField()
    permit_expiry = models.DateField(null=True, blank=True)
    
    # GPS Tracking
    gps_device_id = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        ordering = ['vehicle_number']
    
    def __str__(self):
        return f"{self.vehicle_number} ({self.get_vehicle_type_display()})"


class Driver(models.Model):
    """
    Driver information and license details.
    """
    # Personal Info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    aadhar_number = models.CharField(max_length=12, blank=True)
    photo = models.ImageField(upload_to='drivers/', blank=True)
    
    # License Details
    license_number = models.CharField(max_length=30, unique=True)
    license_type = models.CharField(max_length=20)  # LMV, HMV, etc.
    license_expiry = models.DateField()
    
    # Employment
    date_of_joining = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Assigned vehicle
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drivers'
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Route(models.Model):
    """
    Transport routes with stops.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # Distance and timing
    total_distance_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    estimated_time_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated journey time in minutes"
    )
    
    # Assigned vehicle and driver
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes'
    )
    
    # Morning pickup time from first stop
    morning_start_time = models.TimeField()
    # Evening departure from school
    evening_start_time = models.TimeField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routes'
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class RouteStop(models.Model):
    """
    Individual stops on a route.
    """
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='stops'
    )
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    
    # GPS coordinates
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    
    # Order and timing
    stop_order = models.PositiveIntegerField()
    morning_time = models.TimeField(help_text="Pickup time in morning")
    evening_time = models.TimeField(help_text="Drop time in evening")
    
    # Fee for this stop
    monthly_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    class Meta:
        db_table = 'route_stops'
        verbose_name = 'Route Stop'
        verbose_name_plural = 'Route Stops'
        unique_together = ['route', 'stop_order']
        ordering = ['route', 'stop_order']
    
    def __str__(self):
        return f"{self.route.code} - Stop {self.stop_order}: {self.name}"


class StudentTransport(models.Model):
    """
    Student transport assignment.
    """
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='transport'
    )
    route_stop = models.ForeignKey(
        RouteStop,
        on_delete=models.CASCADE,
        related_name='students'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear',
        on_delete=models.CASCADE,
        related_name='transport_assignments'
    )
    
    # Transport type
    class TransportType(models.TextChoices):
        BOTH = 'both', 'Both Ways'
        MORNING_ONLY = 'morning', 'Morning Only'
        EVENING_ONLY = 'evening', 'Evening Only'
    
    transport_type = models.CharField(
        max_length=20,
        choices=TransportType.choices,
        default=TransportType.BOTH
    )
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_transports'
        verbose_name = 'Student Transport'
        verbose_name_plural = 'Student Transports'
        ordering = ['route_stop__route', 'route_stop__stop_order']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.route_stop.route.name}"
