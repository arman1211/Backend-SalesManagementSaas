from rest_framework import serializers

from apps.warranty_certificates.models import WarrantyCertificate
from apps.warranty_certificates.serializers.warranty_certificate_item import (
    WarrantyCertificateItemSerializer,
)
from apps.warranty_certificates.services.warranty_certificate import WarrantyCertificateService


class WarrantyCertificateListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    items_summary = serializers.SerializerMethodField()

    class Meta:
        model = WarrantyCertificate
        fields = (
            "id",
            "reference_number",
            "certificate_date",
            "customer",
            "customer_name",
            "project_name",
            "items_summary",
            "finishing_date",
            "warranty_end_date",
            "warranty_months",
            "status",
            "created_at",
        )

    def get_items_summary(self, obj):
        return obj.items_summary()


class WarrantyCertificateDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    entity_name = serializers.CharField(source="entity.name", read_only=True)
    service_report_ref = serializers.CharField(
        source="service_report.reference_number",
        read_only=True,
        default=None,
    )
    items = WarrantyCertificateItemSerializer(many=True, read_only=True)

    class Meta:
        model = WarrantyCertificate
        fields = (
            "id",
            "reference_number",
            "certificate_date",
            "entity",
            "entity_name",
            "customer",
            "customer_name",
            "service_report",
            "service_report_ref",
            "project_name",
            "attention_person",
            "drn",
            "finishing_date",
            "warranty_end_date",
            "customer_lpo",
            "service_report_reference",
            "work_title",
            "work_description",
            "warranty_months",
            "warranty_statement",
            "signatory_name",
            "signatory_phone",
            "signatory_email",
            "status",
            "notes",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "reference_number", "warranty_end_date", "created_at", "updated_at")


class WarrantyCertificateWriteSerializer(serializers.ModelSerializer):
    items = WarrantyCertificateItemSerializer(many=True)

    class Meta:
        model = WarrantyCertificate
        fields = (
            "entity",
            "customer",
            "service_report",
            "certificate_date",
            "project_name",
            "attention_person",
            "drn",
            "finishing_date",
            "customer_lpo",
            "service_report_reference",
            "work_title",
            "work_description",
            "warranty_months",
            "warranty_statement",
            "signatory_name",
            "signatory_phone",
            "signatory_email",
            "notes",
            "items",
        )

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Add at least one product or equipment item.")
        for index, item in enumerate(items, start=1):
            if not item.get("product_name", "").strip():
                raise serializers.ValidationError(
                    f"Item {index}: product name is required."
                )
        return items

    def validate_service_report(self, service_report):
        if not service_report:
            return service_report
        request = self.context["request"]
        if service_report.tenant_id != request.user.tenant_id:
            raise serializers.ValidationError("Service report does not belong to your organization.")
        return service_report

    def create(self, validated_data):
        request = self.context["request"]
        items = validated_data.pop("items")
        service_report = validated_data.pop("service_report", None)
        entity = validated_data.pop("entity")
        customer = validated_data.pop("customer")

        if service_report:
            entity = service_report.entity
            customer = service_report.customer

        certificate = WarrantyCertificateService.create(
            tenant=request.user.tenant,
            user=request.user,
            entity=entity,
            customer=customer,
            service_report=service_report,
            items=items,
            **validated_data,
        )

        if service_report:
            WarrantyCertificateService.populate_from_service_report(certificate, service_report)
            if certificate.finishing_date:
                certificate.warranty_end_date = certificate.compute_warranty_end_date()
            if not certificate.warranty_statement:
                certificate.warranty_statement = certificate.build_default_warranty_statement()
            certificate.save()

        return certificate

    def update(self, instance, validated_data):
        if instance.status != WarrantyCertificate.Status.DRAFT:
            raise serializers.ValidationError("Only draft warranty certificates can be edited.")

        items = validated_data.pop("items", None)
        service_report = validated_data.pop("service_report", serializers.empty)
        if service_report is not serializers.empty and service_report:
            WarrantyCertificateService.populate_from_service_report(instance, service_report)
            validated_data.pop("entity", None)
            validated_data.pop("customer", None)

        return WarrantyCertificateService.update(instance, items=items, **validated_data)
