

from django.contrib import admin
from .models import Product, CartItem, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price_vnd',
        'product_type',
        'rating',
        'sold_count',
        'is_featured',
        'category',
    )

    list_filter = ('product_type', 'category', 'is_featured')
    search_fields = ('name',)
    list_editable = ('product_type', 'sold_count')

    @admin.display(description='GIÁ (VND)', ordering='price')
    def price_vnd(self, obj):
        return f"{obj.price:,.0f}".replace(",", ".") + " ₫"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_amount')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
