from django.db import models

from apps.core.models.base import TimeStampedModel, UUIDModel


class CustomerContact(UUIDModel, TimeStampedModel):
    """Contact person linked to a customer."""

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return f"{self.name} ({self.customer.name})"
