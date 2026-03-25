from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    # product_set

    def __str__(self):
        return f"Discount: {self.discount * -100}%"

    class Meta:
        ordering = ["discount"]


class Collection(models.Model):
    title = models.CharField(max_length=255)

    # Revers One to Many Relationship
    featured_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)

    # One to Many Relationship
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name="products"
    )

    # Many to Many Relationship
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self):
        return self.title


class Costumer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"
    MEMBERSHIP = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=False)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP, default=MEMBERSHIP_BRONZE
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    # Onr to One Relationship
    costumer = models.OneToOneField(
        Costumer, on_delete=models.CASCADE, primary_key=True
    )

    def __str__(self):
        return self.city

    class Meta:
        ordering = ["city"]


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETED = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETED, "Completed"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS, default=PAYMENT_STATUS_PENDING
    )

    # One to Many Relationship
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT)

    def __str__(self):
        return f"ORDER-{self.id}-{self.payment_status}"

    class Meta:
        ordering = ["placed_at"]


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField()
    unite_price = models.DecimalField(max_digits=6, decimal_places=2)

    # One to Many Relationship
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems"
    )

    def __str__(self):
        return f"ITEM-{self.id}"

    class Meta:
        ordering = ["unite_price"]


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CART-{self.id}"

    class Meta:
        ordering = ["created_at"]


class CartItem(models.Model):
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    # One to Many Relationship
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return f"CART-ITEM-{self.id}"

    class Meta:
        ordering = ["quantity"]
        unique_together = [["cart", "product"]]


class Review(models.Model):
    name = models.CharField(max_length=255)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
