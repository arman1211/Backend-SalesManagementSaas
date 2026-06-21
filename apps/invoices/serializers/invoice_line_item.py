from rest_framework import serializers

from apps.invoices.models import InvoiceLineItem


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ("id", "serial_number", "description", "unit_price", "quantity", "line_total")
        read_only_fields = ("id", "line_total")
