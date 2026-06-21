from rest_framework import serializers

from apps.invoices.models import Invoice
from apps.invoices.serializers.invoice_line_item import InvoiceLineItemSerializer
from apps.invoices.services.invoice import InvoiceService
from apps.payments.models import Payment


class InvoicePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id", "payment_date", "amount", "payment_method",
            "reference_number", "bank_name", "notes",
        )


class InvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id", "invoice_number", "invoice_date", "due_date",
            "customer", "customer_name", "customer_lpo", "drn",
            "grand_total", "balance_amount", "payment_status",
            "exceed_days", "status", "created_at",
        )


class InvoiceDetailSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    payments = InvoicePaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    entity_name = serializers.CharField(source="entity.name", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id", "invoice_number", "previous_invoice_number",
            "invoice_date", "due_date", "entity", "entity_name",
            "customer", "customer_name", "quotation", "service_report",
            "customer_lpo", "drn", "quotation_reference", "status",
            "subtotal", "discount_amount", "discount_percent",
            "net_total", "vat_rate", "vat_amount", "grand_total",
            "payment_terms_days", "payment_terms_text", "notes",
            "retention_rate", "retention_amount", "amount_received",
            "balance_amount", "late_fee_rate", "late_fee_amount",
            "net_amount_due", "exceed_days", "payment_status", "remarks",
            "line_items", "payments", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "invoice_number", "subtotal", "net_total", "vat_amount",
            "grand_total", "retention_amount", "amount_received",
            "balance_amount", "late_fee_amount", "net_amount_due",
            "exceed_days", "payment_status", "due_date",
            "created_at", "updated_at",
        )


class InvoiceWriteSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = (
            "entity", "customer", "quotation", "service_report",
            "invoice_date", "previous_invoice_number",
            "customer_lpo", "drn", "quotation_reference",
            "discount_amount", "discount_percent", "vat_rate",
            "payment_terms_days", "payment_terms_text", "notes",
            "retention_rate", "late_fee_rate", "line_items",
        )

    def create(self, validated_data):
        line_items = validated_data.pop("line_items")
        request = self.context["request"]
        return InvoiceService.create(
            tenant=request.user.tenant,
            user=request.user,
            line_items=line_items,
            **validated_data,
        )

    def update(self, instance, validated_data):
        if instance.status not in (Invoice.Status.DRAFT,):
            raise serializers.ValidationError("Only draft invoices can be edited.")
        line_items = validated_data.pop("line_items", None)
        return InvoiceService.update(instance, line_items=line_items, **validated_data)
