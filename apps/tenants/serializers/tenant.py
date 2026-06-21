from rest_framework import serializers

from apps.tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = (
            "id",
            "name",
            "slug",
            "legal_name",
            "trn",
            "email",
            "phone",
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "logo",
            "status",
            "default_vat_rate",
            "default_payment_terms_days",
            "default_retention_rate",
            "default_late_fee_rate",
            "bank_name",
            "bank_account_name",
            "bank_account_number",
            "bank_iban",
            "default_payment_terms_text",
            "default_terms_and_conditions",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "status", "created_at", "updated_at")
