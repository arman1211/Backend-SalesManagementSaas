from rest_framework import serializers

from apps.warranty_certificates.models import WarrantyCertificateItem


class WarrantyCertificateItemSerializer(serializers.ModelSerializer):
    location_display = serializers.CharField(read_only=True)

    class Meta:
        model = WarrantyCertificateItem
        fields = (
            "id",
            "serial_number",
            "product_name",
            "specification",
            "identifier",
            "location",
            "site_reference",
            "location_display",
        )
        read_only_fields = ("id", "location_display")
