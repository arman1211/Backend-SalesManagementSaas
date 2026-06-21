from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from apps.credit_notes.models import CreditNote
from apps.invoices.models import Invoice
from apps.payments.models import Payment


class ReportService:
    @staticmethod
    def aging_report(tenant):
        today = timezone.localdate()
        unpaid = Invoice.objects.filter(
            tenant=tenant,
            payment_status=Invoice.PaymentStatus.UNPAID,
        ).exclude(status=Invoice.Status.CANCELLED)

        buckets = {
            "current": Decimal("0.00"),
            "1_30": Decimal("0.00"),
            "31_60": Decimal("0.00"),
            "61_90": Decimal("0.00"),
            "over_90": Decimal("0.00"),
        }
        details = []

        for invoice in unpaid.select_related("customer"):
            days = invoice.exceed_days or 0
            amount = invoice.net_amount_due

            if days <= 0:
                buckets["current"] += amount
                bucket = "current"
            elif days <= 30:
                buckets["1_30"] += amount
                bucket = "1_30"
            elif days <= 60:
                buckets["31_60"] += amount
                bucket = "31_60"
            elif days <= 90:
                buckets["61_90"] += amount
                bucket = "61_90"
            else:
                buckets["over_90"] += amount
                bucket = "over_90"

            details.append({
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "customer_name": invoice.customer.name,
                "due_date": invoice.due_date,
                "exceed_days": days,
                "net_amount_due": str(amount),
                "bucket": bucket,
            })

        return {
            "summary": {key: str(value) for key, value in buckets.items()},
            "total_outstanding": str(sum(buckets.values(), Decimal("0.00"))),
            "invoices": details,
        }

    @staticmethod
    def account_statement(tenant, customer_id, from_date=None, to_date=None):
        from apps.customers.models import Customer

        customer = Customer.objects.get(id=customer_id, tenant=tenant)
        invoices = Invoice.objects.filter(
            tenant=tenant, customer=customer
        ).exclude(status=Invoice.Status.CANCELLED)
        payments = Payment.objects.filter(tenant=tenant, customer=customer)
        credit_notes = CreditNote.objects.filter(
            tenant=tenant, customer=customer, status__in=["issued", "applied"]
        )

        if from_date:
            invoices = invoices.filter(invoice_date__gte=from_date)
            payments = payments.filter(payment_date__gte=from_date)
            credit_notes = credit_notes.filter(credit_note_date__gte=from_date)
        if to_date:
            invoices = invoices.filter(invoice_date__lte=to_date)
            payments = payments.filter(payment_date__lte=to_date)
            credit_notes = credit_notes.filter(credit_note_date__lte=to_date)

        transactions = []
        for inv in invoices:
            transactions.append({
                "date": inv.invoice_date,
                "type": "invoice",
                "reference": f"INV-{inv.invoice_number}",
                "description": f"Tax Invoice #{inv.invoice_number}",
                "debit": str(inv.grand_total),
                "credit": "0.00",
            })
        for pay in payments:
            transactions.append({
                "date": pay.payment_date,
                "type": "payment",
                "reference": pay.reference_number or str(pay.id),
                "description": f"Payment for INV-{pay.invoice.invoice_number}",
                "debit": "0.00",
                "credit": str(pay.amount),
            })
        for cn in credit_notes:
            transactions.append({
                "date": cn.credit_note_date,
                "type": "credit_note",
                "reference": f"CN-{cn.credit_note_number}",
                "description": cn.reason or f"Credit Note #{cn.credit_note_number}",
                "debit": "0.00",
                "credit": str(cn.grand_total),
            })

        transactions.sort(key=lambda row: row["date"])

        balance = Decimal("0.00")
        for row in transactions:
            balance += Decimal(row["debit"]) - Decimal(row["credit"])
            row["balance"] = str(balance)
            row["date"] = row["date"].isoformat()

        total_invoiced = invoices.aggregate(t=Sum("grand_total"))["t"] or Decimal("0.00")
        total_paid = payments.aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        total_credited = credit_notes.aggregate(t=Sum("grand_total"))["t"] or Decimal("0.00")

        return {
            "customer": {"id": str(customer.id), "name": customer.name, "trn": customer.trn},
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
            "transactions": transactions,
            "summary": {
                "total_invoiced": str(total_invoiced),
                "total_paid": str(total_paid),
                "total_credited": str(total_credited),
                "closing_balance": str(total_invoiced - total_paid - total_credited),
            },
        }

    @staticmethod
    def vat_summary(tenant, from_date=None, to_date=None):
        invoices = Invoice.objects.filter(tenant=tenant).exclude(
            status__in=[Invoice.Status.DRAFT, Invoice.Status.CANCELLED]
        )
        credit_notes = CreditNote.objects.filter(
            tenant=tenant, status__in=["issued", "applied"]
        )
        if from_date:
            invoices = invoices.filter(invoice_date__gte=from_date)
            credit_notes = credit_notes.filter(credit_note_date__gte=from_date)
        if to_date:
            invoices = invoices.filter(invoice_date__lte=to_date)
            credit_notes = credit_notes.filter(credit_note_date__lte=to_date)

        inv_vat = invoices.aggregate(t=Sum("vat_amount"))["t"] or Decimal("0.00")
        cn_vat = credit_notes.aggregate(t=Sum("vat_amount"))["t"] or Decimal("0.00")
        inv_net = invoices.aggregate(t=Sum("net_total"))["t"] or Decimal("0.00")
        cn_net = credit_notes.aggregate(t=Sum("subtotal"))["t"] or Decimal("0.00")

        return {
            "invoice_vat_collected": str(inv_vat),
            "credit_note_vat": str(cn_vat),
            "net_vat_payable": str(inv_vat - cn_vat),
            "taxable_sales": str(inv_net - cn_net),
            "invoice_count": invoices.count(),
            "credit_note_count": credit_notes.count(),
        }

    @staticmethod
    def collections_report(tenant, from_date=None, to_date=None):
        payments = Payment.objects.filter(tenant=tenant).select_related("customer", "invoice")
        if from_date:
            payments = payments.filter(payment_date__gte=from_date)
        if to_date:
            payments = payments.filter(payment_date__lte=to_date)

        total = payments.aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        by_method = (
            payments.values("payment_method")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )
        return {
            "total_collected": str(total),
            "payment_count": payments.count(),
            "by_method": [
                {
                    "payment_method": row["payment_method"],
                    "total": str(row["total"]),
                    "count": row["count"],
                }
                for row in by_method
            ],
            "payments": list(
                payments.order_by("-payment_date").values(
                    "id", "payment_date", "amount", "payment_method",
                    "customer__name", "invoice__invoice_number", "reference_number",
                )[:100]
            ),
        }

    @staticmethod
    def sales_summary(tenant, from_date=None, to_date=None):
        invoices = Invoice.objects.filter(tenant=tenant).exclude(
            status__in=[Invoice.Status.DRAFT, Invoice.Status.CANCELLED]
        )
        if from_date:
            invoices = invoices.filter(invoice_date__gte=from_date)
        if to_date:
            invoices = invoices.filter(invoice_date__lte=to_date)

        totals = invoices.aggregate(
            grand_total=Sum("grand_total"),
            net_total=Sum("net_total"),
            vat_total=Sum("vat_amount"),
        )
        by_customer = (
            invoices.values("customer__name")
            .annotate(total=Sum("grand_total"), count=Count("id"))
            .order_by("-total")[:10]
        )
        return {
            "invoice_count": invoices.count(),
            "grand_total": str(totals["grand_total"] or Decimal("0.00")),
            "net_total": str(totals["net_total"] or Decimal("0.00")),
            "vat_total": str(totals["vat_total"] or Decimal("0.00")),
            "top_customers": [
                {
                    "customer_name": row["customer__name"],
                    "total": str(row["total"]),
                    "invoice_count": row["count"],
                }
                for row in by_customer
            ],
        }
