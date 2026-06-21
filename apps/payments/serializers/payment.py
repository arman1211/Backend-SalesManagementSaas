from rest_framework import serializers

from apps.invoices.models import Invoice
from apps.payments.models import Payment
from apps.payments.services.payment import PaymentService


class PaymentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    invoice_number = serializers.IntegerField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id", "payment_date", "amount", "payment_method",
            "reference_number", "customer", "customer_name",
            "invoice", "invoice_number", "created_at",
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    invoice_number = serializers.IntegerField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id", "payment_date", "amount", "payment_method",
            "reference_number", "bank_name", "notes",
            "customer", "customer_name", "invoice", "invoice_number",
            "recorded_by", "created_at", "updated_at",
        )
        read_only_fields = ("id", "customer", "recorded_by", "created_at", "updated_at")


class PaymentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "invoice", "payment_date", "amount",
            "payment_method", "reference_number", "bank_name", "notes",
        )

    def create(self, validated_data):
        request = self.context["request"]
        invoice = validated_data.pop("invoice")
        if invoice.tenant_id != request.user.tenant_id:
            raise serializers.ValidationError("Invoice does not belong to your tenant.")
        if invoice.status == Invoice.Status.DRAFT:
            raise serializers.ValidationError("Finalize the invoice before recording payment.")
        if invoice.status == Invoice.Status.CANCELLED:
            raise serializers.ValidationError("Cannot record payment on a cancelled invoice.")
        return PaymentService.record_payment(
            tenant=request.user.tenant,
            user=request.user,
            invoice=invoice,
            **validated_data,
        )
