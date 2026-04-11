from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from store.models import Costumer, Order


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_costumer_for_new_user(sender, **kwargs):
    if kwargs["created"]:
        Costumer.objects.create(user=kwargs["instance"])


@receiver(pre_save, sender=Order)
def capture_previous_status(sender, instance, **kwargs):
    """Snapshot the previous status before save so post_save can compare."""
    if not instance.pk:
        instance._previous_order_status = None
        return
    try:
        instance._previous_order_status = Order.objects.get(pk=instance.pk).order_status
    except Order.DoesNotExist:
        instance._previous_order_status = None


@receiver(post_save, sender=Order)
def on_order_saved(sender, instance, created, **kwargs):
    # Import here to avoid circular imports
    from store.tasks import (
        send_cash_order_confirmation_email,
        send_order_cancelled_email,
    )

    # Task 2 — new cash order
    if created and instance.payment_method == Order.PAYMENT_METHOD_CASH:
        transaction.on_commit(
            lambda: send_cash_order_confirmation_email.delay(instance.id)
        )
        return

    # Task 3 — order cancelled
    previous = getattr(instance, "_previous_order_status", None)
    if (
        previous != Order.ORDER_STATUS_CANCELLED
        and instance.order_status == Order.ORDER_STATUS_CANCELLED
    ):
        transaction.on_commit(lambda: send_order_cancelled_email.delay(instance.id))
