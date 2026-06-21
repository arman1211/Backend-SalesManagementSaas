from django.contrib import admin

from apps.service_reports.models import ServiceReport


@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ("reference_number", "customer", "report_date", "job_status", "status")
