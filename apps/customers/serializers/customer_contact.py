from rest_framework import serializers

from apps.customers.models import CustomerContact


class CustomerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerContact
        fields = (
            "id",
            "name",
            "designation",
            "email",
            "phone",
            "is_primary",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
