from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Prefetch

from . import models


@shared_task
def send_order_confirmation_email(order_id: int):
    order = (
        models.Order.objects.select_related("costumer__user")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=models.OrderItem.objects.select_related("product"),
            )
        )
        .filter(pk=order_id)
        .first()
    )
    if not order:
        return

    costumer = order.costumer
    recipient = costumer.user.email
    if not recipient:
        return

    store_name = "Frontstore"
    items = list(order.items.all())
    total = sum(item.quantity * item.unite_price for item in items)
    total_display = f"{total:.2f} MAD"

    address = getattr(costumer, "address", None)

    text_lines = [
        f"{store_name} - Order Confirmation",
        "",
        f"Order ID: {order.id}",
        "",
        "Items:",
    ]
    for item in items:
        line_total = item.quantity * item.unite_price
        text_lines.append(
            f"- {item.product.title} x{item.quantity} @ {item.unite_price} = "
            f"{line_total:.2f} MAD"
        )
    text_lines += [
        "",
        f"Total: {total_display}",
    ]
    if address:
        text_lines += [
            "",
            "Shipping Address:",
            f"{address.street}",
            f"{address.city}",
        ]
    if costumer.phone:
        text_lines += ["", f"Phone: {costumer.phone}"]
    text_lines += ["", "We'll notify you when it ships.", "", "Thank you!"]

    subject = f"Order #{order.id} confirmation"
    message = "\n".join(text_lines)

    item_rows = ""
    for item in items:
        line_total = item.quantity * item.unite_price
        item_rows += (
            "<tr>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #eee;'>"
            f"{item.product.title}</td>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #eee;"
            f"text-align:center;'>{item.quantity}</td>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #eee;"
            f"text-align:right;'>{item.unite_price:.2f} MAD</td>"
            f"<td style='padding:6px 8px;border-bottom:1px solid #eee;"
            f"text-align:right;'>{line_total:.2f} MAD</td>"
            "</tr>"
        )

    address_html = ""
    if address:
        address_html = (
            "<p style='margin:8px 0 0;'>"
            "<strong>Shipping Address</strong><br>"
            f"{address.street}<br>{address.city}"
            "</p>"
        )
    phone_html = ""
    if costumer.phone:
        phone_html = (
            f"<p style='margin:8px 0 0;'><strong>Phone</strong><br>"
            f"{costumer.phone}</p>"
        )

    header_row = (
        "<tr>"
        "<th style='text-align:left;padding:6px 8px;"
        "border-bottom:2px solid #111;'>"
        "Item</th>"
        "<th style='text-align:center;padding:6px 8px;"
        "border-bottom:2px solid #111;'>"
        "Qty</th>"
        "<th style='text-align:right;padding:6px 8px;"
        "border-bottom:2px solid #111;'>"
        "Unit</th>"
        "<th style='text-align:right;padding:6px 8px;"
        "border-bottom:2px solid #111;'>"
        "Line</th>"
        "</tr>"
    )

    html_message = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.5;color:#111;">
      <h2 style="margin:0 0 12px;">{store_name} - Order Confirmation</h2>
      <p style="margin:0 0 12px;">Order ID: <strong>{order.id}</strong></p>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          {header_row}
        </thead>
        <tbody>
          {item_rows}
        </tbody>
      </table>
      <p style="margin:12px 0 0;"><strong>Total: {total_display}</strong></p>
      {address_html}
      {phone_html}
      <p style="margin:12px 0 0;">We'll notify you when it ships.</p>
      <p style="margin:12px 0 0;">Thank you!</p>
    </div>
    """

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[recipient],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
