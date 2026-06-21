from django.db import models
from django.utils import timezone

from apps.core.models.base import UUIDModel
from apps.core.models.mixins import TenantScopedModel


class ServiceReport(UUIDModel, TenantScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        COMPLETED = "completed", "Completed"
        SENT = "sent", "Sent"
        INVOICED = "invoiced", "Invoiced"
        ARCHIVED = "archived", "Archived"

    class JobStatus(models.TextChoices):
        OPERATIONAL = "operational", "Operational"
        UNDER_OBSERVATION = "under_observation", "Under Observation"
        NEEDS_FOLLOWUP = "needs_followup", "Needs Follow-up"

    entity = models.ForeignKey(
        "tenants.CompanyEntity",
        on_delete=models.PROTECT,
        related_name="service_reports",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="service_reports",
    )
    quotation = models.ForeignKey(
        "quotations.Quotation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_reports",
    )
    reference_number = models.CharField(max_length=50, blank=True)
    report_date = models.DateField(default=timezone.localdate)
    customer_lpo = models.CharField(max_length=100, blank=True)
    drn = models.CharField(max_length=100, blank=True)
    attention_person = models.CharField(max_length=150, blank=True)
    equipment_details = models.TextField(blank=True)
    work_description = models.TextField(blank=True)
    site_location = models.CharField(max_length=255, blank=True)
    equipment_id = models.CharField(max_length=100, blank=True)
    work_start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    quotation_reference = models.CharField(max_length=100, blank=True)
    recommendations = models.TextField(blank=True)
    job_status = models.CharField(
        max_length=30,
        choices=JobStatus.choices,
        default=JobStatus.OPERATIONAL,
    )
    technician_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_reports_created",
    )

    class Meta:
        ordering = ["-report_date", "-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "reference_number"]),
        ]

    def __str__(self):
        return self.reference_number or str(self.id)
