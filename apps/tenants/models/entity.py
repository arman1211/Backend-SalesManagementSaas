from django.db import models

from apps.core.models.base import TimeStampedModel, UUIDModel


class CompanyEntity(UUIDModel, TimeStampedModel):
    """Legal business entity under a tenant (e.g. two Paramount companies)."""

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="entities",
    )
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    trn = models.CharField("Tax Registration Number", max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True, default="Abu Dhabi")
    country = models.CharField(max_length=100, blank=True, default="UAE")
    logo = models.ImageField(upload_to="entities/logos/", blank=True, null=True)
    is_default = models.BooleanField(default=False)
    quotation_prefix = models.CharField(max_length=20, blank=True, default="QTN")
    invoice_prefix = models.CharField(max_length=20, blank=True, default="INV")
    credit_note_prefix = models.CharField(max_length=20, blank=True, default="CN")
    service_report_prefix = models.CharField(max_length=20, blank=True, default="SR")
    next_invoice_number = models.PositiveIntegerField(default=1)
    next_quotation_number = models.PositiveIntegerField(default=1)
    next_credit_note_number = models.PositiveIntegerField(default=1)
    next_service_report_number = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["name"]
        verbose_name = "Company Entity"
        verbose_name_plural = "Company Entities"

    def __str__(self):
        return self.name
