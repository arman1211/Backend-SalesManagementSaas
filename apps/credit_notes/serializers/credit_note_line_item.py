from rest_framework import serializers

from apps.credit_notes.models import CreditNoteLineItem


class CreditNoteLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNoteLineItem
        fields = ("id", "serial_number", "description", "unit_price", "quantity", "line_total")
        read_only_fields = ("id", "line_total")
