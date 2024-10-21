# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    Customer, 
    Cake, 
    CakeCustomization, 
    Cart, 
    CartItem, 
    Order
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone_no', 'city', 'total_orders')
    search_fields = ('email', 'first_name', 'last_name', 'phone_no')
    list_filter = ('city', 'state')
    ordering = ('-created_at',)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def total_orders(self, obj):
        return Order.objects.filter(customer=obj).count()
    
    total_orders.short_description = 'Total Orders'

@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'flavour', 'size', 'price', 'available', 'display_image')
    list_filter = ('available', 'flavour', 'size')
    search_fields = ('name', 'flavour')
    list_editable = ('available', 'price')
    ordering = ('name',)

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;"/>',
                obj.image.url
            )
        return "No Image"
    
    display_image.short_description = 'Image'

@admin.register(CakeCustomization)
class CakeCustomizationAdmin(admin.ModelAdmin):
    list_display = ('cake', 'customer', 'message', 'egg_version', 'shape')
    list_filter = ('egg_version', 'shape')
    search_fields = ('message', 'customer__email', 'cake__name')
    ordering = ('-created_at',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    raw_id_fields = ('cake', 'customization')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total_items', 'total_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('customer__email', 'customer__first_name')
    inlines = [CartItemInline]
    ordering = ('-created_at',)

    def total_items(self, obj):
        return obj.items.count()
    
    total_items.short_description = 'Total Items'

class OrderItemInline(admin.TabularInline):
    model = Order.items.through
    extra = 1
    raw_id_fields = ('cake',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'customer', 
        'total_price', 
        'order_status', 
        'payment_status', 
        'order_date'
    )
    list_filter = (
        'order_status', 
        'payment_status', 
        'payment_method', 
        'order_date'
    )
    search_fields = (
        'customer__email', 
        'customer__first_name', 
        'delivery_address'
    )
    readonly_fields = ('order_date', 'created_at')
    inlines = [OrderItemInline]
    ordering = ('-order_date',)
    date_hierarchy = 'order_date'

    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'delivery_address')
        }),
        ('Order Details', {
            'fields': ('total_price', 'order_date', 'order_status')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_method')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('items', 'customer')
        return queryset

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of completed orders
        if obj and obj.order_status == 'completed':
            return False
        return super().has_delete_permission(request, obj)

# Register any remaining models
admin.site.register(CartItem)

# Custom admin site configuration
admin.site.site_header = 'SweetSpot Administration'
admin.site.site_title = 'SweetSpot Admin Portal'
admin.site.index_title = 'Welcome to SweetSpot Admin Portal'