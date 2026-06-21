from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.models.base import UUIDModel
from apps.core.models.mixins import AbstractLineItem, TenantScopedModel


class Quotation(UUIDModel, TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"
        CONVERTED = "converted", "Converted"
        CANCELLED = "cancelled", "Cancelled"

    entity = models.ForeignKey(
        "tenants.CompanyEntity",
        on_delete=models.PROTECT,
        related_name="quotations",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="quotations",
    )
    reference_number = models.CharField(max_length=50, blank=True)
    quotation_date = models.DateField(default=timezone.localdate)
    valid_until = models.DateField(null=True, blank=True)
    attention_person = models.CharField(max_length=150, blank=True)
    customer_lpo = models.CharField(max_length=100, blank=True)
    site_reference = models.CharField(max_length=100, blank=True)
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
    validity_days = models.PositiveIntegerField(default=30)
    terms_and_conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations_created",
    )

    class Meta:
        ordering = ["-quotation_date", "-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "reference_number"]),
        ]

    def __str__(self):
        return self.reference_number or str(self.id)


class QuotationLineItem(AbstractLineItem):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="line_items",
    )

    class Meta:
        ordering = ["serial_number"]
