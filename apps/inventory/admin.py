"""
Admin configuration for inventory app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ItemCategory, StoreLocation, Vendor, Item,
    PurchaseOrder, PurchaseOrderItem, StockTransaction, Asset
)


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'items_count']
    list_filter = ['parent']
    search_fields = ['name', 'code']
    autocomplete_fields = ['parent']
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'


@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'building', 'room_number', 'in_charge', 'items_count']
    search_fields = ['name', 'code', 'building']
    autocomplete_fields = ['in_charge']
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'phone', 'city', 'gstin', 'is_active']
    list_filter = ['is_active', 'city', 'state']
    search_fields = ['name', 'code', 'contact_person', 'gstin']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Info', {
            'fields': (('code', 'name'), 'contact_person')
        }),
        ('Contact', {
            'fields': (('phone', 'alt_phone'), 'email')
        }),
        ('Address', {
            'fields': ('address', ('city', 'state', 'pincode'))
        }),
        ('Tax Details', {
            'fields': (('gstin', 'pan'),)
        }),
        ('Bank Details', {
            'fields': ('bank_name', ('account_number', 'ifsc_code')),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'category',
        'item_type',
        'unit',
        'current_stock',
        'stock_status',
        'unit_price_display',
        'is_active'
    ]
    list_filter = ['item_type', 'category', 'store_location', 'is_active']
    search_fields = ['name', 'code', 'description']
    autocomplete_fields = ['category', 'store_location', 'preferred_vendor']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Item Info', {
            'fields': (('code', 'name'), 'description', ('category', 'item_type'))
        }),
        ('Units & Pricing', {
            'fields': (('unit', 'unit_price'),)
        }),
        ('Stock Levels', {
            'fields': (('current_stock', 'minimum_stock', 'reorder_level'),)
        }),
        ('Location & Vendor', {
            'fields': (('store_location', 'preferred_vendor'),)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def stock_status(self, obj):
        if obj.current_stock <= obj.minimum_stock:
            return format_html('<span style="color: red; font-weight: bold;">Low Stock</span>')
        elif obj.current_stock <= obj.reorder_level:
            return format_html('<span style="color: orange;">Reorder</span>')
        return format_html('<span style="color: green;">OK</span>')
    stock_status.short_description = 'Stock Status'
    
    def unit_price_display(self, obj):
        return f"₹{obj.unit_price:,.2f}"
    unit_price_display.short_description = 'Unit Price'


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    autocomplete_fields = ['item']
    readonly_fields = ['total_price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'order_date',
        'vendor',
        'status_colored',
        'total_display',
        'created_by'
    ]
    list_filter = ['status', 'order_date', 'vendor']
    search_fields = ['order_number', 'vendor__name']
    autocomplete_fields = ['vendor', 'created_by', 'approved_by']
    date_hierarchy = 'order_date'
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ['subtotal', 'total_amount', 'approved_at', 'created_at']
    
    fieldsets = (
        ('Order Info', {
            'fields': (('order_number', 'order_date'), 'vendor')
        }),
        ('Amounts', {
            'fields': (('subtotal', 'tax_amount', 'discount_amount'), 'total_amount')
        }),
        ('Delivery', {
            'fields': (('expected_delivery', 'received_date'),)
        }),
        ('Status', {
            'fields': ('status', 'remarks')
        }),
        ('Workflow', {
            'fields': (('created_by', 'approved_by'), 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'approved': 'purple',
            'ordered': 'orange',
            'received': 'green',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def total_display(self, obj):
        return f"₹{obj.total_amount:,.2f}"
    total_display.short_description = 'Total'


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date',
        'item',
        'transaction_type_colored',
        'quantity_display',
        'reference_number',
        'created_by'
    ]
    list_filter = ['transaction_type', 'transaction_date', 'item__category']
    search_fields = ['item__name', 'reference_number', 'issued_to_person']
    autocomplete_fields = ['item', 'purchase_order', 'created_by']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction', {
            'fields': ('item', ('transaction_type', 'transaction_date'))
        }),
        ('Quantity & Price', {
            'fields': (('quantity', 'unit_price'),)
        }),
        ('Reference', {
            'fields': ('reference_number', 'purchase_order')
        }),
        ('Issue Details', {
            'fields': (('issued_to_department', 'issued_to_person'),),
            'classes': ('collapse',)
        }),
        ('Remarks', {
            'fields': ('remarks',)
        }),
    )
    
    def transaction_type_colored(self, obj):
        colors = {
            'purchase': 'green',
            'issue': 'blue',
            'return': 'purple',
            'adjustment': 'orange',
            'damage': 'red',
            'opening': 'gray',
        }
        color = colors.get(obj.transaction_type, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_transaction_type_display()
        )
    transaction_type_colored.short_description = 'Type'
    
    def quantity_display(self, obj):
        if obj.quantity > 0:
            return format_html('<span style="color: green;">+{}</span>', obj.quantity)
        return format_html('<span style="color: red;">{}</span>', obj.quantity)
    quantity_display.short_description = 'Qty'


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_code',
        'item',
        'serial_number',
        'purchase_date',
        'purchase_price_display',
        'current_value_display',
        'status_colored',
        'assigned_to'
    ]
    list_filter = ['status', 'item__category', 'department', 'purchase_date']
    search_fields = ['asset_code', 'serial_number', 'item__name']
    autocomplete_fields = ['item', 'vendor', 'location', 'assigned_to']
    date_hierarchy = 'purchase_date'
    
    fieldsets = (
        ('Asset Info', {
            'fields': (('asset_code', 'item'), 'serial_number')
        }),
        ('Purchase', {
            'fields': (('purchase_date', 'purchase_price'), ('vendor', 'warranty_expiry'))
        }),
        ('Location & Assignment', {
            'fields': (('location', 'department'), 'assigned_to')
        }),
        ('Depreciation', {
            'fields': (('useful_life_years', 'salvage_value'),)
        }),
        ('Status', {
            'fields': ('status', 'remarks')
        }),
    )
    
    def purchase_price_display(self, obj):
        return f"₹{obj.purchase_price:,.2f}"
    purchase_price_display.short_description = 'Purchase Price'
    
    def current_value_display(self, obj):
        return f"₹{obj.current_value:,.2f}"
    current_value_display.short_description = 'Current Value'
    
    def status_colored(self, obj):
        colors = {
            'active': 'green',
            'under_repair': 'orange',
            'disposed': 'gray',
            'lost': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
