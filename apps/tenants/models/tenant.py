from django.db import models

from apps.core.models.base import TimeStampedModel, UUIDModel


class Tenant(UUIDModel, TimeStampedModel):
    """A company/organization using the SaaS platform."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRIAL = "trial", "Trial"
        SUSPENDED = "suspended", "Suspended"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    legal_name = models.CharField(max_length=255, blank=True)
    trn = models.CharField("Tax Registration Number", max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True, default="Abu Dhabi")
    country = models.CharField(max_length=100, blank=True, default="UAE")
    logo = models.ImageField(upload_to="tenants/logos/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TRIAL,
    )
    default_vat_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.05)
    default_payment_terms_days = models.PositiveIntegerField(default=30)
    default_retention_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.10
    )
    default_late_fee_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.03
    )
    bank_name = models.CharField(max_length=150, blank=True)
    bank_account_name = models.CharField(max_length=150, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_iban = models.CharField(max_length=50, blank=True)
    default_payment_terms_text = models.TextField(blank=True)
    default_terms_and_conditions = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return self.name
