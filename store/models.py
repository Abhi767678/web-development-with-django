from django.db import models
from django.contrib.auth.models import AbstractUser


# ─── 1. CUSTOM USER ───────────────────────────────────────────
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    phone   = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role    = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.role})"


# ─── 2. CATEGORY ──────────────────────────────────────────────
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description   = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name


# ─── 3. BRAND ─────────────────────────────────────────────────
class Brand(models.Model):
    brand_name  = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.brand_name


# ─── 4. PRODUCT ───────────────────────────────────────────────
class Product(models.Model):
    product_name   = models.CharField(max_length=150)
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand          = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    price          = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    description    = models.TextField(blank=True, null=True)
    product_image  = models.ImageField(upload_to='products/', blank=True, null=True)
    added_by       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name


# ─── 5. CART ──────────────────────────────────────────────────
class Cart(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity   = models.IntegerField(default=1)
    added_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.product.product_name}"

    def get_total(self):
        return self.product.price * self.quantity


# ─── 6. ORDER ─────────────────────────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


# ─── 7. ORDER ITEMS ───────────────────────────────────────────
class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price    = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} × {self.quantity}"

    def get_total(self):
        return self.price * self.quantity