import io

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_receipt_pdf(order, payment):
    """
    Generates a receipt PDF in memory and returns raw bytes.
    We build it in memory (BytesIO) so we never touch the filesystem —
    no temp files to clean up, no permissions to worry about.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=20,
        spaceAfter=4 * mm,
    )
    story.append(Paragraph("Payment Receipt", title_style))
    story.append(
        Paragraph(
            f"Order #{order.id} &nbsp;·&nbsp; {timezone.now().strftime('%B %d, %Y')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 8 * mm))

    # ── Customer Info ─────────────────────────────────────────────
    story.append(Paragraph("Billed To", styles["Heading3"]))
    story.append(Paragraph(order.costumer.user.get_full_name(), styles["Normal"]))
    story.append(Paragraph(order.costumer.user.email, styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    # ── Order Items Table ─────────────────────────────────────────
    story.append(Paragraph("Order Summary", styles["Heading3"]))
    story.append(Spacer(1, 3 * mm))

    table_data = [["Item", "Qty", "Unit Price", "Total"]]
    for item in order.items.select_related("product").all():
        table_data.append(
            [
                item.product.title,
                str(item.quantity),
                f"{item.unite_price:.2f} {payment.currency.upper()}",
                f"{item.total_price:.2f} {payment.currency.upper()}",
            ]
        )

    table = Table(table_data, colWidths=[90 * mm, 20 * mm, 35 * mm, 35 * mm])
    table.setStyle(
        TableStyle(
            [
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d2a44")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                # Body rows
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f5f7fa")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce6f6")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 6 * mm))

    # ── Total ─────────────────────────────────────────────────────
    total_style = ParagraphStyle(
        "Total",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Helvetica-Bold",
        alignment=2,  # right align
    )
    story.append(
        Paragraph(
            f"Total Paid: {payment.amount / 100:.2f} {payment.currency.upper()}",
            total_style,
        )
    )
    story.append(Spacer(1, 4 * mm))

    # ── Footer ────────────────────────────────────────────────────
    story.append(
        Paragraph(
            "Thank you for your order. Keep this receipt for your records.",
            styles["Italic"],
        )
    )

    doc.build(story)
    return buffer.getvalue()  # raw PDF bytes
