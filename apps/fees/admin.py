"""
Admin configuration for fees app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import FeeCategory, FeeStructure, FeeDiscount, StudentFee, FeePayment, FeePaymentDetail


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'fee_type', 'is_mandatory', 'is_active']
    list_filter = ['fee_type', 'is_mandatory', 'is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_active']


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'standard', 'fee_category', 'amount_display', 'frequency', 'is_active']
    list_filter = ['academic_year', 'standard', 'fee_category', 'frequency', 'is_active']
    search_fields = ['fee_category__name', 'standard__name']
    list_editable = ['is_active']
    autocomplete_fields = ['academic_year', 'standard', 'fee_category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('academic_year', 'standard', 'fee_category', 'amount')
        }),
        ('Payment Schedule', {
            'fields': ('frequency', 'due_day')
        }),
        ('Late Fee', {
            'fields': (('late_fee_per_day', 'max_late_fee'),),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def amount_display(self, obj):
        return f"₹{obj.amount:,.2f}"
    amount_display.short_description = 'Amount'


@admin.register(FeeDiscount)
class FeeDiscountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_type', 'value', 'is_active']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['name', 'code']
    filter_horizontal = ['applicable_categories']


class FeePaymentDetailInline(admin.TabularInline):
    model = FeePaymentDetail
    extra = 0
    readonly_fields = ['student_fee', 'amount']


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = [
        'student', 
        'fee_category_display',
        'original_amount_display', 
        'discount_amount_display',
        'net_amount_display', 
        'paid_amount_display',
        'balance_display',
        'due_date',
        'status_colored'
    ]
    list_filter = [
        'status', 
        'fee_structure__academic_year',
        'fee_structure__standard',
        'fee_structure__fee_category',
        'due_date'
    ]
    search_fields = [
        'student__first_name', 
        'student__last_name', 
        'student__admission_number'
    ]
    autocomplete_fields = ['student', 'fee_structure', 'discount']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Student & Fee', {
            'fields': ('student', 'fee_structure', ('period_month', 'period_quarter'))
        }),
        ('Amounts', {
            'fields': (
                'original_amount',
                ('discount', 'discount_amount'),
                'net_amount',
                ('paid_amount', 'late_fee')
            )
        }),
        ('Schedule', {
            'fields': ('due_date', 'status')
        }),
        ('Remarks', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        }),
    )
    
    def fee_category_display(self, obj):
        return obj.fee_structure.fee_category.name
    fee_category_display.short_description = 'Fee Category'
    
    def original_amount_display(self, obj):
        return f"₹{obj.original_amount:,.2f}"
    original_amount_display.short_description = 'Original'
    
    def discount_amount_display(self, obj):
        if obj.discount_amount > 0:
            return f"-₹{obj.discount_amount:,.2f}"
        return "-"
    discount_amount_display.short_description = 'Discount'
    
    def net_amount_display(self, obj):
        return f"₹{obj.net_amount:,.2f}"
    net_amount_display.short_description = 'Net Amount'
    
    def paid_amount_display(self, obj):
        return f"₹{obj.paid_amount:,.2f}"
    paid_amount_display.short_description = 'Paid'
    
    def balance_display(self, obj):
        balance = obj.balance_amount
        if balance > 0:
            return format_html('<span style="color: red;">₹{:,.2f}</span>', balance)
        return format_html('<span style="color: green;">₹0.00</span>')
    balance_display.short_description = 'Balance'
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'partial': 'blue',
            'paid': 'green',
            'overdue': 'red',
            'waived': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = [
        'receipt_number', 
        'receipt_date', 
        'student',
        'amount_display', 
        'payment_mode',
        'status',
        'collected_by'
    ]
    list_filter = ['status', 'payment_mode', 'receipt_date']
    search_fields = [
        'receipt_number', 
        'student__first_name', 
        'student__last_name',
        'student__admission_number',
        'transaction_id'
    ]
    date_hierarchy = 'receipt_date'
    autocomplete_fields = ['student', 'collected_by']
    inlines = [FeePaymentDetailInline]
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Receipt Info', {
            'fields': (('receipt_number', 'receipt_date'), 'student')
        }),
        ('Payment', {
            'fields': ('amount', 'payment_mode')
        }),
        ('Cheque/DD Details', {
            'fields': (('cheque_number', 'cheque_date'), 'bank_name'),
            'classes': ('collapse',)
        }),
        ('Online Payment', {
            'fields': ('transaction_id',),
            'classes': ('collapse',)
        }),
        ('Status & Collection', {
            'fields': ('status', 'collected_by', 'remarks')
        }),
    )
    
    def amount_display(self, obj):
        return f"₹{obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
