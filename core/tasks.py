from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .utils import build_receipt_pdf


def _send_email(subject, to, template_name, context, attachments=None):
    """
    Internal helper — renders both HTML and text templates and sends the email.
    attachments: list of (filename, data, mimetype) tuples
    """
    text_content = render_to_string(f"core/emails/{template_name}.txt", context)
    html_content = render_to_string(f"core/emails/{template_name}.html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to],
    )
    email.attach_alternative(html_content, "text/html")

    if attachments:
        for filename, data, mimetype in attachments:
            email.attach(filename, data, mimetype)

    email.send()


# ── Task 1 — Payment Receipt (card payment) ───────────────────────────────────


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_receipt_email(self, order_id, payment_id):
    """
    Sends a payment confirmation email with a PDF receipt attached.
    Triggered after payment_succeeded signal — card payments only.
    Retries up to 3 times with 60s delay if the email server is down.
    """
    from payment.models import Payment
    from store.models import Order

    try:
        order = (
            Order.objects.select_related("costumer__user")
            .prefetch_related("items__product")
            .get(id=order_id)
        )
        payment = Payment.objects.get(id=payment_id)

        pdf_bytes = build_receipt_pdf(order, payment)

        _send_email(
            subject=f"Payment Confirmed — Order #{order.id}",
            to=order.costumer.user.email,
            template_name="payment_receipt",
            context={
                "costumer_name": order.costumer.user.get_full_name(),
                "order": order,
                "payment": payment,
            },
            attachments=[
                (f"receipt-order-{order.id}.pdf", pdf_bytes, "application/pdf")
            ],
        )

    except Exception as exc:
        # Retry on failure — network blip, email server down, etc.
        raise self.retry(exc=exc)


# ── Task 2 — Cash Order Confirmation ─────────────────────────────────────────
