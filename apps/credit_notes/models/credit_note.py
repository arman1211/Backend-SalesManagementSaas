from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.models.base import UUIDModel
from apps.core.models.mixins import AbstractLineItem, TenantScopedModel


class CreditNote(UUIDModel, TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"
        CANCELLED = "cancelled", "Cancelled"

    entity = models.ForeignKey(
        "tenants.CompanyEntity",
        on_delete=models.PROTECT,
        related_name="credit_notes",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="credit_notes",
    )
    original_invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.PROTECT,
        related_name="credit_notes",
    )
    credit_note_number = models.PositiveIntegerField()
    credit_note_date = models.DateField(default=timezone.localdate)
    customer_lpo = models.CharField(max_length=100, blank=True)
    site_reference = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.05"))
    vat_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    payment_terms_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_notes_created",
    )

    class Meta:
        ordering = ["-credit_note_date", "-credit_note_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "entity", "credit_note_number"],
                name="unique_tenant_entity_credit_note_number",
            )
        ]

    def __str__(self):
        return f"CN-{self.credit_note_number}"


class CreditNoteLineItem(AbstractLineItem):
    credit_note = models.ForeignKey(
        CreditNote,
        on_delete=models.CASCADE,
        related_name="line_items",
    )

    class Meta:
        ordering = ["serial_number"]
