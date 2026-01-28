"""
Admin configuration for transport app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle, Driver, Route, RouteStop, StudentTransport


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        'vehicle_number', 
        'vehicle_type', 
        'make', 
        'model',
        'seating_capacity',
        'insurance_status',
        'fitness_status',
        'is_active'
    ]
    list_filter = ['vehicle_type', 'is_active', 'make']
    search_fields = ['vehicle_number', 'registration_number']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Vehicle Info', {
            'fields': (
                'vehicle_number',
                ('vehicle_type', 'seating_capacity'),
                ('make', 'model', 'year')
            )
        }),
        ('Documents', {
            'fields': (
                'registration_number',
                ('insurance_number', 'insurance_expiry'),
                ('fitness_expiry', 'pollution_expiry'),
                'permit_expiry'
            )
        }),
        ('GPS Tracking', {
            'fields': ('gps_device_id',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def insurance_status(self, obj):
        from datetime import date
        if obj.insurance_expiry < date.today():
            return format_html('<span style="color: red;">Expired</span>')
        elif (obj.insurance_expiry - date.today()).days < 30:
            return format_html('<span style="color: orange;">Expiring Soon</span>')
        return format_html('<span style="color: green;">Valid</span>')
    insurance_status.short_description = 'Insurance'
    
    def fitness_status(self, obj):
        from datetime import date
        if obj.fitness_expiry < date.today():
            return format_html('<span style="color: red;">Expired</span>')
        elif (obj.fitness_expiry - date.today()).days < 30:
            return format_html('<span style="color: orange;">Expiring Soon</span>')
        return format_html('<span style="color: green;">Valid</span>')
    fitness_status.short_description = 'Fitness'


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'phone',
        'license_number',
        'license_status',
        'vehicle',
        'is_active'
    ]
    list_filter = ['is_active', 'license_type']
    search_fields = ['first_name', 'last_name', 'phone', 'license_number']
    autocomplete_fields = ['vehicle']
    
    fieldsets = (
        ('Personal Info', {
            'fields': (
                ('first_name', 'last_name'),
                ('phone', 'alternate_phone'),
                'address',
                ('aadhar_number', 'photo')
            )
        }),
        ('License', {
            'fields': (
                ('license_number', 'license_type'),
                'license_expiry'
            )
        }),
        ('Employment', {
            'fields': (
                ('date_of_joining', 'salary'),
                'vehicle'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def license_status(self, obj):
        from datetime import date
        if obj.license_expiry < date.today():
            return format_html('<span style="color: red;">Expired</span>')
        elif (obj.license_expiry - date.today()).days < 30:
            return format_html('<span style="color: orange;">Expiring Soon</span>')
        return format_html('<span style="color: green;">Valid</span>')
    license_status.short_description = 'License Status'


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    fields = ['stop_order', 'name', 'morning_time', 'evening_time', 'monthly_fee']
    ordering = ['stop_order']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'vehicle',
        'driver',
        'total_distance_km',
        'stops_count',
        'students_count',
        'is_active'
    ]
    list_filter = ['is_active', 'vehicle']
    search_fields = ['name', 'code']
    autocomplete_fields = ['vehicle', 'driver']
    inlines = [RouteStopInline]
    
    fieldsets = (
        ('Route Info', {
            'fields': (
                ('code', 'name'),
                'description'
            )
        }),
        ('Timing', {
            'fields': (
                ('morning_start_time', 'evening_start_time'),
                ('total_distance_km', 'estimated_time_minutes')
            )
        }),
        ('Assignment', {
            'fields': (('vehicle', 'driver'),)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def stops_count(self, obj):
        return obj.stops.count()
    stops_count.short_description = 'Stops'
    
    def students_count(self, obj):
        return StudentTransport.objects.filter(
            route_stop__route=obj,
            is_active=True
        ).count()
    students_count.short_description = 'Students'


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ['route', 'stop_order', 'name', 'morning_time', 'evening_time', 'monthly_fee_display']
    list_filter = ['route']
    search_fields = ['name', 'route__name']
    autocomplete_fields = ['route']
    ordering = ['route', 'stop_order']
    
    def monthly_fee_display(self, obj):
        return f"₹{obj.monthly_fee:,.2f}"
    monthly_fee_display.short_description = 'Monthly Fee'


@admin.register(StudentTransport)
class StudentTransportAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'route_display',
        'stop_display',
        'transport_type',
        'monthly_fee_display',
        'is_active'
    ]
    list_filter = ['is_active', 'transport_type', 'route_stop__route', 'academic_year']
    search_fields = [
        'student__first_name',
        'student__last_name',
        'student__admission_number'
    ]
    autocomplete_fields = ['student', 'route_stop', 'academic_year']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Student', {
            'fields': ('student', 'academic_year')
        }),
        ('Route Assignment', {
            'fields': ('route_stop', 'transport_type')
        }),
        ('Duration', {
            'fields': (('start_date', 'end_date'),)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def route_display(self, obj):
        return obj.route_stop.route.name
    route_display.short_description = 'Route'
    
    def stop_display(self, obj):
        return obj.route_stop.name
    stop_display.short_description = 'Stop'
    
    def monthly_fee_display(self, obj):
        return f"₹{obj.route_stop.monthly_fee:,.2f}"
    monthly_fee_display.short_description = 'Monthly Fee'
