from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.core.services.calculations import quantize_money
from apps.invoices.models import Invoice


def refresh_invoice_receivable(invoice: Invoice, save=True):
    """Recalculate retention, balance, overdue days, and late fees."""
    today = timezone.localdate()
    invoice.due_date = invoice.invoice_date + timedelta(days=invoice.payment_terms_days)

    received = invoice.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    invoice.amount_received = quantize_money(received)
    invoice.retention_amount = quantize_money(invoice.grand_total * invoice.retention_rate)

    balance = invoice.grand_total - invoice.retention_amount - invoice.amount_received
    invoice.balance_amount = quantize_money(max(balance, Decimal("0.00")))

    credit_total = invoice.credit_notes.filter(
        status__in=["issued", "applied"]
    ).aggregate(total=Sum("grand_total"))["total"] or Decimal("0.00")
    if credit_total:
        invoice.balance_amount = quantize_money(
            max(invoice.balance_amount - credit_total, Decimal("0.00"))
        )

    if invoice.balance_amount == Decimal("0.00"):
        invoice.payment_status = Invoice.PaymentStatus.PAID
        invoice.exceed_days = 0
        invoice.late_fee_amount = Decimal("0.00")
        if invoice.status not in (Invoice.Status.DRAFT, Invoice.Status.CANCELLED):
            invoice.status = Invoice.Status.PAID
    else:
        invoice.payment_status = Invoice.PaymentStatus.UNPAID
        if invoice.status not in (Invoice.Status.DRAFT, Invoice.Status.CANCELLED):
            if today > invoice.due_date:
                invoice.exceed_days = (today - invoice.due_date).days
                invoice.late_fee_amount = quantize_money(
                    invoice.balance_amount * invoice.late_fee_rate
                )
                invoice.status = Invoice.Status.OVERDUE
            else:
                invoice.exceed_days = 0
                invoice.late_fee_amount = Decimal("0.00")
                if invoice.amount_received > 0:
                    invoice.status = Invoice.Status.PARTIALLY_PAID
                elif invoice.status == Invoice.Status.OVERDUE:
                    invoice.status = Invoice.Status.ISSUED

    invoice.net_amount_due = quantize_money(
        invoice.balance_amount + invoice.late_fee_amount
    )

    if save:
        invoice.save(
            update_fields=[
                "due_date",
                "amount_received",
                "retention_amount",
                "balance_amount",
                "payment_status",
                "exceed_days",
                "late_fee_amount",
                "net_amount_due",
                "status",
                "updated_at",
            ]
        )
    return invoice
