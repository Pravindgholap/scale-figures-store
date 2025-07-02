from django.contrib import admin
from .models import Category, Product, CartItem, Cart, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug':('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    list_filter = ['available', 'created', 'updated', 'category']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    date_hierarchy = 'created'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'date_added']
    list_filter = ['date_added']
    search_fields = ['cart_id']


# NEW: Register the CartItem model with custom admin options
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'active', 'total_price']
    list_filter = ['active', 'cart']
    search_fields = ['product__name', 'cart__cart_id']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'paid', 'created', 'get_total_cost']
    list_filter = ['paid', 'created', 'updated', 'user']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'user__username']
    inlines = [OrderItemInline]
    list_editable = ['paid']
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid')
        }),
        ('Dates', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',) 
        }),
    )
    readonly_fields = ['created', 'updated']