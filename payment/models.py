from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Payment(models.Model):

    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_SUCCEEDED = "S"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS_CANCELLED = "C"
    PAYMENT_STATUS = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_SUCCEEDED, "Succeeded"),
        (PAYMENT_STATUS_FAILED, "Failed"),
        (PAYMENT_STATUS_CANCELLED, "Cancelled"),
    ]

    # The Stripe Payment Intent ID — this is the link between
    # your database and Stripe's servers. Always unique per payment attempt.
    stripe_intent_id = models.CharField(max_length=255, unique=True)

    # Who is paying — nullable in case you support guest checkout later
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )

    # Generic reference to whatever is being paid for.
    # 'object_type' could be 'order', 'subscription', 'donation', etc.
    # 'object_id' is the primary key of that object in its own table.
    # This keeps the payment app independent — no ForeignKey to Order here.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    amount = models.PositiveIntegerField()  # always in cents, just like Stripe
    currency = models.CharField(max_length=10, default="usd")

    status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS,
        default=PAYMENT_STATUS_PENDING,
        db_index=True,
    )

    # Store the full Stripe event for debugging — invaluable when something goes wrong
    stripe_payload = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Payment {self.stripe_intent_id} — {self.status}"
