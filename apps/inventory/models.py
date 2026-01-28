"""
Inventory Management models for School Management System.
Handles assets, stock, purchases, and vendors.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ItemCategory(models.Model):
    """
    Categories for inventory items.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    
    class Meta:
        db_table = 'item_categories'
        verbose_name = 'Item Category'
        verbose_name_plural = 'Item Categories'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class StoreLocation(models.Model):
    """
    Physical storage locations.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    building = models.CharField(max_length=100, blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    in_charge = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_locations'
    )
    
    class Meta:
        db_table = 'store_locations'
        verbose_name = 'Store Location'
        verbose_name_plural = 'Store Locations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Vendor(models.Model):
    """
    Suppliers and vendors.
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    
    # Contact
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    alt_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    
    # Tax details
    gstin = models.CharField(max_length=15, blank=True, help_text="GST Identification Number")
    pan = models.CharField(max_length=10, blank=True)
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendors'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Item(models.Model):
    """
    Inventory items/products.
    """
    class ItemType(models.TextChoices):
        CONSUMABLE = 'consumable', 'Consumable'
        NON_CONSUMABLE = 'non_consumable', 'Non-Consumable'
        ASSET = 'asset', 'Asset'
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    item_type = models.CharField(
        max_length=20,
        choices=ItemType.choices,
        default=ItemType.CONSUMABLE
    )
    
    # Units
    unit = models.CharField(max_length=20, default='Piece', help_text="e.g., Piece, Box, Kg, Liter")
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Stock levels
    minimum_stock = models.PositiveIntegerField(
        default=5,
        help_text="Alert when stock falls below this level"
    )
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text="Recommended stock level for reordering"
    )
    
    # Current stock (calculated from transactions)
    current_stock = models.PositiveIntegerField(default=0)
    
    # Location
    store_location = models.ForeignKey(
        StoreLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    
    # Default vendor
    preferred_vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplied_items'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items'
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock


class PurchaseOrder(models.Model):
    """
    Purchase orders for inventory.
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        APPROVED = 'approved', 'Approved'
        ORDERED = 'ordered', 'Ordered'
        RECEIVED = 'received', 'Received'
        CANCELLED = 'cancelled', 'Cancelled'
    
    order_number = models.CharField(max_length=30, unique=True)
    order_date = models.DateField()
    
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    expected_delivery = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    # Workflow
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_purchase_orders'
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_orders'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_orders'
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-order_date', '-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.vendor.name}"
    
    def calculate_totals(self):
        """Calculate order totals from items."""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()


class PurchaseOrderItem(models.Model):
    """
    Line items in a purchase order.
    """
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='purchase_order_items'
    )
    
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    received_quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'purchase_order_items'
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'
    
    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class StockTransaction(models.Model):
    """
    Tracks all stock movements (in/out).
    """
    class TransactionType(models.TextChoices):
        PURCHASE = 'purchase', 'Purchase'
        ISSUE = 'issue', 'Issue'
        RETURN = 'return', 'Return'
        ADJUSTMENT = 'adjustment', 'Adjustment'
        DAMAGE = 'damage', 'Damage/Loss'
        OPENING = 'opening', 'Opening Stock'
    
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    
    quantity = models.IntegerField(help_text="Positive for in, negative for out")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Reference
    reference_number = models.CharField(max_length=50, blank=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_transactions'
    )
    
    # Issued to (for issue transactions)
    issued_to_department = models.CharField(max_length=100, blank=True)
    issued_to_person = models.CharField(max_length=100, blank=True)
    
    remarks = models.TextField(blank=True)
    
    transaction_date = models.DateField()
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_transactions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_transactions'
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'
        ordering = ['-transaction_date', '-created_at']
    
    def __str__(self):
        return f"{self.item.name} - {self.get_transaction_type_display()} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Update item stock
        if self.pk is None:  # New transaction
            self.item.current_stock += self.quantity
            self.item.save()
        super().save(*args, **kwargs)


class Asset(models.Model):
    """
    Fixed assets with tracking.
    """
    class AssetStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        UNDER_REPAIR = 'under_repair', 'Under Repair'
        DISPOSED = 'disposed', 'Disposed'
        LOST = 'lost', 'Lost'
    
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='assets'
    )
    
    asset_code = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    
    # Purchase info
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets_sold'
    )
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Location and assignment
    location = models.ForeignKey(
        StoreLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    department = models.CharField(max_length=100, blank=True)
    
    # Depreciation
    useful_life_years = models.PositiveIntegerField(default=5)
    salvage_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.ACTIVE
    )
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assets'
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        ordering = ['asset_code']
    
    def __str__(self):
        return f"{self.asset_code} - {self.item.name}"
    
    @property
    def current_value(self):
        """Calculate depreciated value (straight-line method)."""
        from datetime import date
        years_used = (date.today() - self.purchase_date).days / 365
        annual_depreciation = (self.purchase_price - self.salvage_value) / self.useful_life_years
        depreciation = annual_depreciation * min(years_used, self.useful_life_years)
        return max(self.purchase_price - Decimal(str(depreciation)), self.salvage_value)
