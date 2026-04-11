from django.dispatch import receiver

from payment.signals import payment_failed, payment_succeeded
from store.models import Order


@receiver(payment_succeeded)
def on_payment_succeeded(sender, payment_intent_id, metadata, **kwargs):
    """
    When a payment succeeds, core is responsible for
    telling the store to fulfill the order.
    The payment app fired the signal and forgot about it.
    The store model handles the update.
    Core is just the bridge connecting the two.
    """
    print(metadata)
    order_id = metadata.get("object_id")
    if order_id:
        Order.objects.filter(id=order_id).update(
            payment_status=Order.PAYMENT_STATUS_COMPLETED,
        )


@receiver(payment_failed)
def on_payment_failed(sender, payment_intent_id, metadata, **kwargs):
    order_id = metadata.get("order_id")
    if order_id:
        Order.objects.filter(id=order_id).update(
            payment_status=Order.PAYMENT_STATUS_FAILED
        )
