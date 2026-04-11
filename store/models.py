from uuid import uuid4

from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_file_size


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

    class Meta:
        ordering = ["title"]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="store/images", validators=[validate_file_size])


class Costumer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"
    MEMBERSHIP = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    phone = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP, default=MEMBERSHIP_BRONZE
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name


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

    # ── Payment Status ─────────────────────────────────────────────
    # Answers: "has money moved for this order?"
    # Driven entirely by the payment app via signals → core → here
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETED = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETED, "Completed"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    # ── Order Status ───────────────────────────────────────────────
    # Answers: "where is this order in its fulfillment lifecycle?"
    # Driven by your store logic — packing, shipping, delivery, etc.
    ORDER_STATUS_PENDING = "P"
    ORDER_STATUS_PROCESSING = "R"
    ORDER_STATUS_SHIPPED = "S"
    ORDER_STATUS_DELIVERED = "D"
    ORDER_STATUS_CANCELLED = "C"
    ORDER_STATUS = [
        (ORDER_STATUS_PENDING, "Pending"),
        (ORDER_STATUS_PROCESSING, "Processing"),
        (ORDER_STATUS_SHIPPED, "Shipped"),
        (ORDER_STATUS_DELIVERED, "Delivered"),
        (ORDER_STATUS_CANCELLED, "Cancelled"),
    ]

    # ── Payment Method ─────────────────────────────────────────────
    PAYMENT_METHOD_CARD = "CD"
    PAYMENT_METHOD_CASH = "CA"
    PAYMENT_METHOD = [
        (PAYMENT_METHOD_CARD, "Card"),
        (PAYMENT_METHOD_CASH, "Cash"),
    ]

    # ── Fields ────────────────────────────────────────────────────
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS,
        default=PAYMENT_STATUS_PENDING,
    )
    order_status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS,
        default=ORDER_STATUS_PENDING,
    )
    payment_method = models.CharField(
        max_length=2,
        choices=PAYMENT_METHOD,
        null=True,
        blank=True,
    )
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT)

    # ── Mixin contract ────────────────────────────────────────────
    @property
    def total_amount(self):
        result = self.items.aggregate(
            total=models.Sum(
                models.ExpressionWrapper(
                    models.F("quantity") * models.F("unite_price"),
                    output_field=models.DecimalField(),
                )
            )
        )
        return result["total"] or 0

    def is_payable_by(self, user):
        return (
            self.costumer.user_id == user.id
            and self.payment_status == self.PAYMENT_STATUS_PENDING
            and self.order_status != self.ORDER_STATUS_CANCELLED
        )

    @property
    def requires_online_payment(self):
        return self.payment_method == self.PAYMENT_METHOD_CARD

    def __str__(self):
        return f"ORDER-{self.id}-{self.order_status}-{self.payment_status}"

    class Meta:
        ordering = ["placed_at"]


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField()
    unite_price = models.DecimalField(max_digits=6, decimal_places=2)

    # One to Many Relationship
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )

    @property
    def total_price(self):
        return self.quantity * self.unite_price

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
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
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
