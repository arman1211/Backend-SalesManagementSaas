from django.db import models

from apps.core.models.base import TimeStampedModel, UUIDModel


class WarrantyCertificateItem(UUIDModel, TimeStampedModel):
    """A product or equipment row covered by a warranty certificate."""

    certificate = models.ForeignKey(
        "warranty_certificates.WarrantyCertificate",
        on_delete=models.CASCADE,
        related_name="items",
    )
    serial_number = models.PositiveIntegerField(default=1)
    product_name = models.CharField(max_length=255)
    specification = models.CharField(max_length=255, blank=True)
    identifier = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    site_reference = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["serial_number", "created_at"]

    def __str__(self):
        return self.product_name

    @property
    def location_display(self):
        parts = [part for part in (self.location, self.site_reference) if part]
        return " — ".join(parts)
