from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Brand, Product, Cart, Order, OrderItem


# ─── USER ─────────────────────────────────────────────────────
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'role', 'phone', 'is_active')
    list_filter   = ('role',)
    search_fields = ('username', 'email')
    fieldsets     = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone', 'address')}),
    )


# ─── CATEGORY ─────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('category_name', 'description')
    search_fields = ('category_name',)


# ─── BRAND ────────────────────────────────────────────────────
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display  = ('brand_name', 'description')
    search_fields = ('brand_name',)


# ─── PRODUCT ──────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('product_name', 'category', 'brand', 'price', 'stock_quantity', 'created_at')
    list_filter    = ('category', 'brand')
    search_fields  = ('product_name',)
    readonly_fields = ('created_at',)


# ─── CART ─────────────────────────────────────────────────────
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')


# ─── ORDER ITEMS (inline inside Order) ────────────────────────
class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 0
    readonly_fields = ('product', 'quantity', 'price')


# ─── ORDER ────────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter    = ('status',)
    search_fields  = ('user__username',)
    readonly_fields = ('created_at', 'total_amount', 'user', 'shipping_address')
    inlines        = [OrderItemInline]

    # Admin can only update the status
    def get_fields(self, request, obj=None):
        return ['user', 'total_amount', 'status', 'shipping_address', 'created_at']