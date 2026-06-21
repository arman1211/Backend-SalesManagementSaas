from rest_framework import serializers

from apps.quotations.models import Quotation
from apps.quotations.serializers.quotation_line_item import QuotationLineItemSerializer
from apps.quotations.services.quotation import QuotationService


class QuotationListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    entity_name = serializers.CharField(source="entity.name", read_only=True)

    class Meta:
        model = Quotation
        fields = (
            "id", "reference_number", "quotation_date", "valid_until",
            "customer", "customer_name", "entity", "entity_name",
            "grand_total", "status", "created_at",
        )


class QuotationDetailSerializer(serializers.ModelSerializer):
    line_items = QuotationLineItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    entity_name = serializers.CharField(source="entity.name", read_only=True)

    class Meta:
        model = Quotation
        fields = (
            "id", "reference_number", "quotation_date", "valid_until",
            "entity", "entity_name", "customer", "customer_name",
            "attention_person", "customer_lpo", "site_reference", "status",
            "subtotal", "discount_amount", "discount_percent",
            "net_total", "vat_rate", "vat_amount", "grand_total",
            "payment_terms_days", "payment_terms_text", "validity_days",
            "terms_and_conditions", "notes", "line_items",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "reference_number", "subtotal", "net_total",
            "vat_amount", "grand_total", "created_at", "updated_at",
        )


class QuotationWriteSerializer(serializers.ModelSerializer):
    line_items = QuotationLineItemSerializer(many=True)

    class Meta:
        model = Quotation
        fields = (
            "entity", "customer", "quotation_date", "valid_until",
            "attention_person", "customer_lpo", "site_reference",
            "discount_amount", "discount_percent", "vat_rate",
            "payment_terms_days", "payment_terms_text", "validity_days",
            "terms_and_conditions", "notes", "line_items",
        )

    def create(self, validated_data):
        line_items = validated_data.pop("line_items")
        request = self.context["request"]
        return QuotationService.create(
            tenant=request.user.tenant,
            user=request.user,
            line_items=line_items,
            **validated_data,
        )

    def update(self, instance, validated_data):
        if instance.status not in (Quotation.Status.DRAFT,):
            raise serializers.ValidationError("Only draft quotations can be edited.")
        line_items = validated_data.pop("line_items", None)
        return QuotationService.update(instance, line_items=line_items, **validated_data)
