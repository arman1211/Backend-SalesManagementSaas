from rest_framework import serializers

from apps.service_reports.models import ServiceReport
from apps.service_reports.services.service_report import ServiceReportService


class ServiceReportListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = ServiceReport
        fields = (
            "id", "reference_number", "report_date", "customer", "customer_name",
            "customer_lpo", "drn", "job_status", "status", "created_at",
        )


class ServiceReportDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    entity_name = serializers.CharField(source="entity.name", read_only=True)

    class Meta:
        model = ServiceReport
        fields = (
            "id", "reference_number", "report_date", "entity", "entity_name",
            "customer", "customer_name", "quotation", "customer_lpo", "drn",
            "attention_person", "equipment_details", "work_description",
            "site_location", "equipment_id", "work_start_date", "completion_date",
            "quotation_reference", "recommendations", "job_status",
            "technician_name", "status", "notes", "created_at", "updated_at",
        )
        read_only_fields = ("id", "reference_number", "created_at", "updated_at")


class ServiceReportWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReport
        fields = (
            "entity", "customer", "quotation", "report_date",
            "customer_lpo", "drn", "attention_person", "equipment_details",
            "work_description", "site_location", "equipment_id",
            "work_start_date", "completion_date", "quotation_reference",
            "recommendations", "job_status", "technician_name", "notes",
        )

    def create(self, validated_data):
        request = self.context["request"]
        return ServiceReportService.create(
            tenant=request.user.tenant,
            user=request.user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        if instance.status != ServiceReport.Status.DRAFT:
            raise serializers.ValidationError("Only draft service reports can be edited.")
        return ServiceReportService.update(instance, **validated_data)
