from django.db import models

from apps.core.models.base import TimeStampedModel, UUIDModel


class Customer(UUIDModel, TimeStampedModel):
    """Customer master record scoped to a tenant."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        BLOCKED = "blocked", "Blocked"

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="customers",
    )
    customer_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="External customer ID (e.g. 1101 from Excel).",
    )
    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True, default="Abu Dhabi")
    country = models.CharField(max_length=100, blank=True, default="UAE")
    trn = models.CharField("Tax Registration Number", max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    default_payment_terms_days = models.PositiveIntegerField(null=True, blank=True)
    retention_rate = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    late_fee_rate = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "customer_code"],
                condition=models.Q(customer_code__isnull=False),
                name="unique_tenant_customer_code",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "name"]),
        ]

    def __str__(self):
        return self.name
