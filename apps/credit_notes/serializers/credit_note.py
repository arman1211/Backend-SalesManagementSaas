from rest_framework import serializers

from apps.credit_notes.models import CreditNote
from apps.credit_notes.serializers.credit_note_line_item import CreditNoteLineItemSerializer
from apps.credit_notes.services.credit_note import CreditNoteService


class CreditNoteListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    invoice_number = serializers.IntegerField(source="original_invoice.invoice_number", read_only=True)

    class Meta:
        model = CreditNote
        fields = (
            "id", "credit_note_number", "credit_note_date",
            "customer", "customer_name", "original_invoice", "invoice_number",
            "grand_total", "status", "created_at",
        )


class CreditNoteDetailSerializer(serializers.ModelSerializer):
    line_items = CreditNoteLineItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    invoice_number = serializers.IntegerField(source="original_invoice.invoice_number", read_only=True)

    class Meta:
        model = CreditNote
        fields = (
            "id", "credit_note_number", "credit_note_date",
            "entity", "customer", "customer_name",
            "original_invoice", "invoice_number",
            "customer_lpo", "site_reference", "reason", "status",
            "subtotal", "vat_rate", "vat_amount", "grand_total",
            "payment_terms_text", "notes", "line_items",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "credit_note_number", "subtotal", "vat_amount",
            "grand_total", "created_at", "updated_at",
        )


class CreditNoteWriteSerializer(serializers.ModelSerializer):
    line_items = CreditNoteLineItemSerializer(many=True, required=False)

    class Meta:
        model = CreditNote
        fields = (
            "original_invoice", "credit_note_date", "site_reference",
            "reason", "payment_terms_text", "notes", "line_items",
        )

    def create(self, validated_data):
        line_items = validated_data.pop("line_items", None)
        request = self.context["request"]
        invoice = validated_data.pop("original_invoice")
        return CreditNoteService.create_from_invoice(
            invoice=invoice,
            user=request.user,
            line_items=line_items,
            **validated_data,
        )
