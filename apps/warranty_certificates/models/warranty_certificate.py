import calendar

from django.db import models
from django.utils import timezone

from apps.core.models.base import UUIDModel
from apps.core.models.mixins import TenantScopedModel


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)


class WarrantyCertificate(UUIDModel, TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        ARCHIVED = "archived", "Archived"

    entity = models.ForeignKey(
        "tenants.CompanyEntity",
        on_delete=models.PROTECT,
        related_name="warranty_certificates",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="warranty_certificates",
    )
    service_report = models.ForeignKey(
        "service_reports.ServiceReport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warranty_certificates",
    )
    reference_number = models.CharField(max_length=50, blank=True)
    certificate_date = models.DateField(default=timezone.localdate)
    project_name = models.CharField(max_length=255, blank=True)
    attention_person = models.CharField(max_length=150, blank=True)
    drn = models.CharField(max_length=100, blank=True)
    finishing_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    customer_lpo = models.CharField(max_length=100, blank=True)
    service_report_reference = models.CharField(max_length=100, blank=True)
    work_title = models.CharField(max_length=255, blank=True)
    work_description = models.TextField(blank=True)
    warranty_months = models.PositiveIntegerField(default=6)
    warranty_statement = models.TextField(blank=True)
    signatory_name = models.CharField(max_length=150, blank=True)
    signatory_phone = models.CharField(max_length=30, blank=True)
    signatory_email = models.EmailField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warranty_certificates_created",
    )

    class Meta:
        ordering = ["-certificate_date", "-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "reference_number"]),
        ]

    def __str__(self):
        return self.reference_number or str(self.id)

    def compute_warranty_end_date(self):
        if not self.finishing_date:
            return None
        return add_months(self.finishing_date, self.warranty_months)

    def items_summary(self):
        names = [item.product_name for item in self.items.all() if item.product_name]
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        return f"{names[0]} +{len(names) - 1} more"

    def build_default_warranty_statement(self):
        items = list(self.items.all())
        if items:
            if len(items) == 1:
                equipment = items[0].product_name
                if items[0].specification:
                    equipment = f"{equipment} ({items[0].specification})"
            else:
                equipment = "the above listed products/equipment"
        else:
            equipment = "the above listed products/equipment"

        customer_name = self.customer.name if self.customer_id else "the customer"
        months = self.warranty_months
        month_label = "Month" if months == 1 else "Months"
        return (
            f"We hereby confirm that all work we performed for {equipment} is "
            f"guaranteed for {months} {month_label} from the date of completion, "
            f"and we will repair any defective work at no additional charge to "
            f"{customer_name}."
        )
