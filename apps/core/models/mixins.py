from decimal import Decimal

from django.db import models

from apps.core.models.base import TimeStampedModel


class TenantScopedModel(TimeStampedModel):
    """Abstract base for records scoped to a tenant."""

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True


class AbstractLineItem(TimeStampedModel):
    """Shared line-item fields for quotations, invoices, credit notes."""

    serial_number = models.PositiveIntegerField(default=1)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        abstract = True

    def calculate_line_total(self):
        return (self.unit_price * self.quantity).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        self.line_total = self.calculate_line_total()
        super().save(*args, **kwargs)
