from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):

    CATEGORY_CHOICES = [
        ('hot', 'Giảm giá sốc'),
        ('featured', 'Sản phẩm nổi bật'),
        ('new', 'Sản phẩm mới'),
        ('normal', 'Thông thường'),
    ]

    PRODUCT_TYPE_CHOICES = [
        ('ball', 'Bóng chuyền'),
        ('shoes', 'Giày bóng chuyền'),
        ('clothing', 'Quần áo bóng chuyền'),
        ('accessories', 'Phụ kiện'),
    ]

    # Danh mục sản phẩm
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='accessories',
        verbose_name='Danh mục sản phẩm'
    )

    # Thông tin sản phẩm
    name = models.CharField(max_length=255)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh sản phẩm'
    )

    # Sản phẩm nổi bật
    is_featured = models.BooleanField(default=False)

    # Loại sản phẩm
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='normal'
    )

    # Phần trăm giảm giá
    discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name='Phần trăm giảm giá'
    )

    # Đánh giá và lượt bán
    rating = models.FloatField(default=0)

    sold_count = models.IntegerField(default=0)

    # Tính giá sau khi giảm
    def final_price(self):
        discount = Decimal(str(self.discount_percent))

        return self.price * (
            Decimal('1') - discount / Decimal('100')
        )

    # Giới hạn phần trăm giảm giá từ 0 đến 100
    def save(self, *args, **kwargs):

        self.discount_percent = max(
            0,
            min(int(self.discount_percent), 100)
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        """Tổng giá của mặt hàng trong giỏ (có áp dụng giảm giá)."""
        return self.quantity * self.product.final_price()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Đơn hàng #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá tại thời điểm mua

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product} x {self.quantity}"
