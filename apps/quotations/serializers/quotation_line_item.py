from rest_framework import serializers

from apps.quotations.models import QuotationLineItem


class QuotationLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLineItem
        fields = ("id", "serial_number", "description", "unit_price", "quantity", "line_total")
        read_only_fields = ("id", "line_total")
