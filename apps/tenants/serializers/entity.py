from rest_framework import serializers

from apps.tenants.models import CompanyEntity


class CompanyEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEntity
        fields = (
            "id", "name", "legal_name", "trn", "email", "phone",
            "address_line_1", "address_line_2", "city", "country", "logo",
            "is_default", "quotation_prefix", "invoice_prefix",
            "credit_note_prefix", "service_report_prefix", "warranty_prefix",
            "next_invoice_number", "next_quotation_number",
            "next_credit_note_number", "next_service_report_number",
            "next_warranty_number",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "next_invoice_number", "next_quotation_number",
            "next_credit_note_number", "next_service_report_number",
            "next_warranty_number",
            "created_at", "updated_at",
        )
