from apps.core.services.documents import sync_line_items
from apps.core.services.numbering import get_next_sequence
from apps.warranty_certificates.models import WarrantyCertificate, WarrantyCertificateItem


class WarrantyCertificateService:
    @staticmethod
    def _apply_computed_fields(certificate, **data):
        for field, value in data.items():
            setattr(certificate, field, value)

        if certificate.finishing_date and (
            "finishing_date" in data
            or "warranty_months" in data
            or not certificate.warranty_end_date
        ):
            certificate.warranty_end_date = certificate.compute_warranty_end_date()

        return certificate

    @staticmethod
    def _sync_items(certificate, items):
        if items is not None:
            sync_line_items(
                certificate,
                items,
                WarrantyCertificateItem,
                "certificate",
                existing_qs=certificate.items.all(),
            )
        if not certificate.warranty_statement:
            certificate.warranty_statement = certificate.build_default_warranty_statement()

    @staticmethod
    def create(tenant, user, entity, customer, items, service_report=None, **data):
        certificate = WarrantyCertificate(
            tenant=tenant,
            entity=entity,
            customer=customer,
            created_by=user,
            service_report=service_report,
        )
        WarrantyCertificateService._apply_computed_fields(certificate, **data)
        certificate.save()

        WarrantyCertificateService._sync_items(certificate, items)
        certificate.save(update_fields=["warranty_statement", "updated_at"])

        if not certificate.reference_number:
            seq = get_next_sequence(entity, "next_warranty_number")
            prefix = entity.warranty_prefix or "WC"
            certificate.reference_number = f"{prefix}-{seq}"
            certificate.save(update_fields=["reference_number", "updated_at"])

        if not certificate.signatory_name and user:
            certificate.signatory_name = user.full_name
            if not certificate.signatory_phone:
                certificate.signatory_phone = user.phone
            if not certificate.signatory_email:
                certificate.signatory_email = user.email
            certificate.save(
                update_fields=[
                    "signatory_name",
                    "signatory_phone",
                    "signatory_email",
                    "updated_at",
                ]
            )

        return certificate

    @staticmethod
    def update(certificate, items=None, **data):
        if certificate.status != WarrantyCertificate.Status.DRAFT:
            raise ValueError("Only draft warranty certificates can be edited.")
        WarrantyCertificateService._apply_computed_fields(certificate, **data)
        certificate.save()
        WarrantyCertificateService._sync_items(certificate, items)
        certificate.save()
        return certificate

    @staticmethod
    def issue(certificate):
        if certificate.status != WarrantyCertificate.Status.DRAFT:
            raise ValueError("Only draft warranty certificates can be issued.")
        if not certificate.finishing_date:
            raise ValueError("Finishing date is required before issuing.")
        if not certificate.items.exists():
            raise ValueError("Add at least one product/equipment item before issuing.")
        if not certificate.work_description:
            raise ValueError("Work description is required before issuing.")

        if not certificate.warranty_end_date:
            certificate.warranty_end_date = certificate.compute_warranty_end_date()
        if not certificate.warranty_statement:
            certificate.warranty_statement = certificate.build_default_warranty_statement()

        certificate.status = WarrantyCertificate.Status.ISSUED
        certificate.save()
        return certificate

    @staticmethod
    def populate_from_service_report(certificate, service_report):
        """Pre-fill empty certificate fields from a linked service report."""
        certificate.service_report = service_report
        certificate.customer = service_report.customer
        certificate.entity = service_report.entity

        defaults = {
            "attention_person": service_report.attention_person,
            "customer_lpo": service_report.customer_lpo,
            "drn": service_report.drn,
            "service_report_reference": service_report.reference_number,
            "finishing_date": service_report.completion_date,
            "work_description": service_report.work_description,
            "work_title": (service_report.equipment_details or "")[:255],
        }
        for field, value in defaults.items():
            if value and not getattr(certificate, field):
                setattr(certificate, field, value)

        if certificate.items.count() == 0 and (
            service_report.equipment_details or service_report.equipment_id or service_report.site_location
        ):
            WarrantyCertificateItem.objects.create(
                certificate=certificate,
                serial_number=1,
                product_name=(service_report.equipment_details or "Equipment")[:255],
                specification="",
                identifier=service_report.equipment_id or "",
                location=service_report.site_location or "",
                site_reference="",
            )

        return certificate
