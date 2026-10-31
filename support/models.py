from django.db import models


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    price_brl = models.DecimalField(max_digits=12, decimal_places=2)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField()
    stock_quantity = models.IntegerField()
    status = models.CharField(max_length=30)
    specs = models.JSONField(default=dict)
    created_at = models.DateField()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Customer(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=40)
    email = models.EmailField()
    city = models.CharField(max_length=120)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    order_date = models.DateField()
    status = models.CharField(max_length=30)
    total_brl = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=40)
    tracking_code = models.CharField(max_length=40, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-order_date", "-id"]

    def __str__(self) -> str:
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_per_order",
            )
        ]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"


class Promotion(models.Model):
    id = models.IntegerField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="promotions")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_active", "product__name"]

    def __str__(self) -> str:
        return f"{self.description} - {self.product.name}"

