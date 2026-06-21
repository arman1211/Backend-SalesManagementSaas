from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.models.base import UUIDModel
from apps.core.models.mixins import AbstractLineItem, TenantScopedModel


class Invoice(UUIDModel, TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        SENT = "sent", "Sent"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"
        CREDITED = "credited", "Credited"

    class PaymentStatus(models.TextChoices):
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"

    entity = models.ForeignKey(
        "tenants.CompanyEntity",
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    quotation = models.ForeignKey(
        "quotations.Quotation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    service_report = models.ForeignKey(
        "service_reports.ServiceReport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    invoice_number = models.PositiveIntegerField()
    previous_invoice_number = models.PositiveIntegerField(null=True, blank=True)
    invoice_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    customer_lpo = models.CharField(max_length=100, blank=True)
    drn = models.CharField("Delivery Reference Number", max_length=100, blank=True)
    quotation_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    net_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.05"))
    vat_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    payment_terms_days = models.PositiveIntegerField(default=30)
    payment_terms_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    # Receivable fields (Excel Payments sheet logic)
    retention_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.10"))
    retention_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    amount_received = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    balance_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    late_fee_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.03"))
    late_fee_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    net_amount_due = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    exceed_days = models.IntegerField(default=0)
    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices_created",
    )

    class Meta:
        ordering = ["-invoice_date", "-invoice_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "entity", "invoice_number"],
                name="unique_tenant_entity_invoice_number",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "payment_status"]),
            models.Index(fields=["tenant", "invoice_date"]),
            models.Index(fields=["tenant", "customer"]),
        ]

    def __str__(self):
        return f"INV-{self.invoice_number}"


class InvoiceLineItem(AbstractLineItem):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="line_items",
    )

    class Meta:
        ordering = ["serial_number"]
