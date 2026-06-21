from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from apps.invoices.models import Invoice
from apps.payments.models import Payment
from apps.quotations.models import Quotation


class DashboardService:
    @staticmethod
    def get_summary(tenant):
        today = timezone.localdate()
        month_start = today.replace(day=1)

        invoices = Invoice.objects.filter(tenant=tenant).exclude(
            status=Invoice.Status.CANCELLED
        )
        unpaid = invoices.filter(payment_status=Invoice.PaymentStatus.UNPAID)
        overdue = invoices.filter(status=Invoice.Status.OVERDUE)

        outstanding = unpaid.aggregate(total=Sum("balance_amount"))["total"] or Decimal("0.00")
        overdue_amount = overdue.aggregate(total=Sum("net_amount_due"))["total"] or Decimal("0.00")
        month_revenue = invoices.filter(
            invoice_date__gte=month_start,
            status__in=[
                Invoice.Status.ISSUED,
                Invoice.Status.PAID,
                Invoice.Status.PARTIALLY_PAID,
                Invoice.Status.OVERDUE,
            ],
        ).aggregate(total=Sum("grand_total"))["total"] or Decimal("0.00")

        month_collected = Payment.objects.filter(
            tenant=tenant, payment_date__gte=month_start
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        top_debtors = (
            unpaid.values("customer_id", "customer__name")
            .annotate(balance=Sum("balance_amount"), invoice_count=Count("id"))
            .order_by("-balance")[:5]
        )

        return {
            "total_outstanding": str(outstanding),
            "total_overdue": str(overdue_amount),
            "unpaid_invoice_count": unpaid.count(),
            "overdue_invoice_count": overdue.count(),
            "month_revenue": str(month_revenue),
            "month_collected": str(month_collected),
            "quotation_pipeline": {
                "draft": Quotation.objects.filter(tenant=tenant, status=Quotation.Status.DRAFT).count(),
                "sent": Quotation.objects.filter(tenant=tenant, status=Quotation.Status.SENT).count(),
                "accepted": Quotation.objects.filter(tenant=tenant, status=Quotation.Status.ACCEPTED).count(),
            },
            "recent_invoices": list(
                invoices.order_by("-created_at")[:10].values(
                    "id", "invoice_number", "customer__name", "grand_total",
                    "payment_status", "invoice_date",
                )
            ),
            "recent_payments": list(
                Payment.objects.filter(tenant=tenant).order_by("-created_at")[:10].values(
                    "id", "amount", "payment_date", "customer__name",
                    "invoice_id", "invoice__invoice_number",
                )
            ),
            "top_debtors": [
                {
                    "customer_id": str(row["customer_id"]),
                    "customer_name": row["customer__name"],
                    "balance": str(row["balance"]),
                    "invoice_count": row["invoice_count"],
                }
                for row in top_debtors
            ],
        }
