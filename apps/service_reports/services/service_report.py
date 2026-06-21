from apps.core.services.numbering import get_next_sequence
from apps.service_reports.models import ServiceReport


class ServiceReportService:
    @staticmethod
    def create(tenant, user, entity, customer, **data):
        report = ServiceReport.objects.create(
            tenant=tenant,
            entity=entity,
            customer=customer,
            created_by=user,
            **data,
        )
        if not report.reference_number:
            seq = get_next_sequence(entity, "next_service_report_number")
            report.reference_number = f"{entity.service_report_prefix}-{seq}"
            report.save(update_fields=["reference_number", "updated_at"])
        return report

    @staticmethod
    def update(report, **data):
        if report.status != ServiceReport.Status.DRAFT:
            raise ValueError("Only draft service reports can be edited.")
        for field, value in data.items():
            setattr(report, field, value)
        report.save()
        return report

    @staticmethod
    def complete(report):
        report.status = ServiceReport.Status.COMPLETED
        report.save(update_fields=["status", "updated_at"])
        return report
