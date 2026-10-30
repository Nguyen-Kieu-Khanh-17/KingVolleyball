

from django.contrib import admin
from .models import Product, CartItem, Order, OrderItem

admin.site.site_header = "King Volleyball - Quản Trị Hệ Thống"
admin.site.site_title = "King Volleyball Admin Portal"
admin.site.index_title = "Bảng Điều Khiển Quản Trị Viên"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price_vnd',
        'discount_percent',
        'product_type',
        'rating',
        'sold_count',
        'is_featured',
        'category',
    )
    list_filter = ('product_type', 'category', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('product_type', 'discount_percent', 'sold_count', 'is_featured')

    @admin.display(description='GIÁ (VND)', ordering='price')
    def price_vnd(self, obj):
        return f"{obj.price:,.0f}".replace(",", ".") + " ₫"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'item_total')

    def item_total(self, obj):
        if obj.id:
            return f"{obj.total_price():,.0f} ₫"
        return "0 ₫"
    item_total.short_description = "Thành tiền"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_amount_vnd', 'item_count')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'id')
    inlines = [OrderItemInline]

    @admin.display(description='Tổng tiền (VND)', ordering='total_amount')
    def total_amount_vnd(self, obj):
        return f"{obj.total_amount:,.0f} ₫"

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Số món'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__created_at',)
    search_fields = ('product__name', 'order__id')
