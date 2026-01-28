"""
Admin configuration for library app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import BookCategory, BookRack, Book, LibraryMember, BookIssue, LibrarySetting


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'books_count']
    search_fields = ['name', 'code']
    
    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Books'


@admin.register(BookRack)
class BookRackAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location', 'books_count']
    search_fields = ['name', 'code']
    
    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'category',
        'total_copies',
        'available_display',
        'price_display',
        'is_active'
    ]
    list_filter = ['category', 'language', 'is_active', 'rack']
    search_fields = ['title', 'author', 'isbn', 'publisher']
    autocomplete_fields = ['category', 'rack']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Book Details', {
            'fields': (
                'title',
                ('author', 'publisher'),
                ('edition', 'publication_year'),
                'isbn'
            )
        }),
        ('Classification', {
            'fields': (('category', 'rack'), 'language')
        }),
        ('Physical Details', {
            'fields': (('pages', 'price'), 'cover_image')
        }),
        ('Stock', {
            'fields': (('total_copies', 'available_copies'),)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def available_display(self, obj):
        if obj.available_copies == 0:
            return format_html('<span style="color: red;">0 / {}</span>', obj.total_copies)
        elif obj.available_copies < obj.total_copies / 2:
            return format_html('<span style="color: orange;">{} / {}</span>', 
                             obj.available_copies, obj.total_copies)
        return format_html('<span style="color: green;">{} / {}</span>', 
                         obj.available_copies, obj.total_copies)
    available_display.short_description = 'Available'
    
    def price_display(self, obj):
        return f"₹{obj.price:,.2f}"
    price_display.short_description = 'Price'


@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = [
        'membership_number',
        'user',
        'member_type',
        'books_issued_display',
        'max_books_allowed',
        'is_active'
    ]
    list_filter = ['member_type', 'is_active']
    search_fields = ['membership_number', 'user__first_name', 'user__last_name']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Member Info', {
            'fields': ('user', 'member_type', 'membership_number')
        }),
        ('Limits', {
            'fields': (('max_books_allowed', 'max_days_allowed'),)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def books_issued_display(self, obj):
        count = obj.books_issued_count
        if count >= obj.max_books_allowed:
            return format_html('<span style="color: red;">{}</span>', count)
        return count
    books_issued_display.short_description = 'Books Issued'


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = [
        'book',
        'member',
        'issue_date',
        'due_date',
        'return_date',
        'status_colored',
        'overdue_display',
        'fine_display'
    ]
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = [
        'book__title',
        'member__user__first_name',
        'member__user__last_name',
        'member__membership_number'
    ]
    autocomplete_fields = ['book', 'member', 'issued_by', 'returned_to']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Issue Info', {
            'fields': ('book', 'member', 'issued_by')
        }),
        ('Dates', {
            'fields': (('issue_date', 'due_date'), 'return_date')
        }),
        ('Return', {
            'fields': ('status', 'returned_to', 'remarks')
        }),
        ('Fine', {
            'fields': (('fine_amount', 'fine_paid'),)
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'issued': 'blue',
            'returned': 'green',
            'lost': 'red',
            'damaged': 'orange',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    def overdue_display(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: red;">{} days</span>',
                obj.days_overdue
            )
        elif obj.status == 'issued':
            return format_html('<span style="color: green;">No</span>')
        return '-'
    overdue_display.short_description = 'Overdue'
    
    def fine_display(self, obj):
        if obj.fine_amount > 0:
            if obj.fine_paid:
                return format_html(
                    '<span style="color: green;">₹{:,.2f} (Paid)</span>',
                    obj.fine_amount
                )
            return format_html(
                '<span style="color: red;">₹{:,.2f}</span>',
                obj.fine_amount
            )
        return '-'
    fine_display.short_description = 'Fine'


@admin.register(LibrarySetting)
class LibrarySettingAdmin(admin.ModelAdmin):
    list_display = ['fine_per_day', 'max_fine_amount', 'lost_book_penalty_percentage']
    
    def has_add_permission(self, request):
        # Only allow one settings record
        return not LibrarySetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
