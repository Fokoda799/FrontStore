from django.db import transaction
from django.dispatch import receiver

from core.tasks import send_payment_receipt_email
from payment.models import Payment
from payment.signals import payment_failed, payment_succeeded
from store.models import Order


@receiver(payment_succeeded)
def on_payment_succeeded(sender, stripe_intent_id, metadata, **kwargs):
    order_id = metadata.get("object_id")
    print("payment sent")
    if not order_id:
        return

    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            return

        if order.payment_status == Order.PAYMENT_STATUS_COMPLETED:
            return

        order.payment_status = Order.PAYMENT_STATUS_COMPLETED
        order.order_status = Order.ORDER_STATUS_PROCESSING
        order.save()

    # Dispatch email task AFTER the transaction commits —
    # we don't want to queue an email for a rollback that never saved
    payment = Payment.objects.get(stripe_intent_id=stripe_intent_id)
    transaction.on_commit(
        lambda: send_payment_receipt_email.delay(order.id, payment.id)
    )


@receiver(payment_failed)
def on_payment_failed(sender, payment_intent_id, metadata, **kwargs):
    order_id = metadata.get("order_id")
    if order_id:
        Order.objects.filter(id=order_id).update(
            payment_status=Order.PAYMENT_STATUS_FAILED
        )
