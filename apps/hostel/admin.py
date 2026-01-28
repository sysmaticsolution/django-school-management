"""
Admin configuration for hostel app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Hostel, HostelRoom, HostelAllocation, MessMenu, HostelVisitor, LeavePass


class HostelRoomInline(admin.TabularInline):
    model = HostelRoom
    extra = 0
    fields = ['room_number', 'floor', 'room_type', 'bed_count', 'current_occupancy', 'is_available']


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'hostel_type',
        'total_rooms',
        'beds_display',
        'monthly_fee_display',
        'warden',
        'is_active'
    ]
    list_filter = ['hostel_type', 'is_active']
    search_fields = ['name', 'code']
    autocomplete_fields = ['warden']
    inlines = [HostelRoomInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': (('name', 'code'), 'hostel_type', 'address')
        }),
        ('Capacity', {
            'fields': (('total_rooms', 'total_beds'),)
        }),
        ('Management', {
            'fields': ('warden', 'phone')
        }),
        ('Fees', {
            'fields': ('monthly_fee',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def beds_display(self, obj):
        available = obj.available_beds
        total = obj.total_beds
        if available == 0:
            return format_html('<span style="color: red;">{} / {} (Full)</span>', available, total)
        elif available < total * 0.2:
            return format_html('<span style="color: orange;">{} / {}</span>', available, total)
        return format_html('<span style="color: green;">{} / {}</span>', available, total)
    beds_display.short_description = 'Available Beds'
    
    def monthly_fee_display(self, obj):
        return f"₹{obj.monthly_fee:,.2f}"
    monthly_fee_display.short_description = 'Monthly Fee'


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = [
        'room_number',
        'hostel',
        'floor',
        'room_type',
        'occupancy_display',
        'amenities_display',
        'additional_fee_display',
        'is_available'
    ]
    list_filter = ['hostel', 'room_type', 'floor', 'is_available', 'has_ac', 'has_attached_bathroom']
    search_fields = ['room_number', 'hostel__name']
    autocomplete_fields = ['hostel']
    
    fieldsets = (
        ('Room Info', {
            'fields': ('hostel', ('room_number', 'floor'), 'room_type')
        }),
        ('Capacity', {
            'fields': (('bed_count', 'current_occupancy'),)
        }),
        ('Amenities', {
            'fields': (
                ('has_attached_bathroom', 'has_ac'),
                ('has_wardrobe', 'has_study_table')
            )
        }),
        ('Fees & Notes', {
            'fields': ('additional_fee', 'remarks')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
    )
    
    def occupancy_display(self, obj):
        if obj.is_full:
            return format_html('<span style="color: red;">{}/{} (Full)</span>', 
                             obj.current_occupancy, obj.bed_count)
        return f"{obj.current_occupancy}/{obj.bed_count}"
    occupancy_display.short_description = 'Occupancy'
    
    def amenities_display(self, obj):
        amenities = []
        if obj.has_ac:
            amenities.append('AC')
        if obj.has_attached_bathroom:
            amenities.append('Attached Bath')
        return ', '.join(amenities) if amenities else 'Basic'
    amenities_display.short_description = 'Amenities'
    
    def additional_fee_display(self, obj):
        if obj.additional_fee > 0:
            return f"+₹{obj.additional_fee:,.0f}"
        return "-"
    additional_fee_display.short_description = 'Extra Fee'


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'room',
        'bed_number',
        'allocation_date',
        'monthly_fee_display',
        'is_active'
    ]
    list_filter = ['is_active', 'room__hostel', 'academic_year', 'allocation_date']
    search_fields = ['student__first_name', 'student__last_name', 'room__room_number']
    autocomplete_fields = ['student', 'room', 'academic_year']
    date_hierarchy = 'allocation_date'
    
    fieldsets = (
        ('Student & Room', {
            'fields': ('student', 'room', 'bed_number')
        }),
        ('Duration', {
            'fields': ('academic_year', ('allocation_date', 'vacating_date'))
        }),
        ('Fee', {
            'fields': ('monthly_fee',)
        }),
        ('Status', {
            'fields': ('is_active', 'remarks')
        }),
    )
    
    def monthly_fee_display(self, obj):
        return f"₹{obj.monthly_fee:,.2f}"
    monthly_fee_display.short_description = 'Monthly Fee'


@admin.register(MessMenu)
class MessMenuAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'day', 'meal_type', 'menu_preview', 'timing']
    list_filter = ['hostel', 'day', 'meal_type']
    search_fields = ['menu_items']
    
    def menu_preview(self, obj):
        return obj.menu_items[:50] + '...' if len(obj.menu_items) > 50 else obj.menu_items
    menu_preview.short_description = 'Menu'


@admin.register(HostelVisitor)
class HostelVisitorAdmin(admin.ModelAdmin):
    list_display = [
        'visitor_name',
        'student',
        'relationship',
        'phone',
        'visit_date',
        'check_in_time',
        'check_out_time',
        'approved_by'
    ]
    list_filter = ['visit_date', 'student__hostel_allocations__room__hostel']
    search_fields = ['visitor_name', 'student__first_name', 'student__last_name', 'phone']
    autocomplete_fields = ['student', 'approved_by']
    date_hierarchy = 'visit_date'
    
    fieldsets = (
        ('Student', {
            'fields': ('student',)
        }),
        ('Visitor Details', {
            'fields': (
                'visitor_name',
                ('relationship', 'phone'),
                ('id_proof_type', 'id_proof_number')
            )
        }),
        ('Visit Timing', {
            'fields': ('visit_date', ('check_in_time', 'check_out_time'))
        }),
        ('Purpose & Remarks', {
            'fields': ('purpose', 'remarks')
        }),
        ('Approval', {
            'fields': ('approved_by',)
        }),
    )


@admin.register(LeavePass)
class LeavePassAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'leave_type',
        'from_date',
        'to_date',
        'destination',
        'status_colored',
        'approved_by'
    ]
    list_filter = ['status', 'leave_type', 'from_date']
    search_fields = ['student__first_name', 'student__last_name', 'destination']
    autocomplete_fields = ['student', 'approved_by']
    date_hierarchy = 'from_date'
    
    fieldsets = (
        ('Student & Leave Type', {
            'fields': ('student', 'leave_type')
        }),
        ('Duration', {
            'fields': (('from_date', 'from_time'), ('to_date', 'to_time'))
        }),
        ('Destination', {
            'fields': ('destination', 'address', 'contact_phone')
        }),
        ('Reason', {
            'fields': ('reason',)
        }),
        ('Approval', {
            'fields': ('status', ('approved_by', 'approved_at'), 'rejection_reason')
        }),
        ('Actual Return', {
            'fields': (('actual_return_date', 'actual_return_time'),),
            'classes': ('collapse',)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'returned': 'blue',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
