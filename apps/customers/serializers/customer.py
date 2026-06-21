from rest_framework import serializers

from apps.customers.models import Customer
from apps.customers.serializers.customer_contact import CustomerContactSerializer


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "customer_code",
            "name",
            "trn",
            "email",
            "phone",
            "city",
            "status",
            "created_at",
        )


class CustomerDetailSerializer(serializers.ModelSerializer):
    contacts = CustomerContactSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "customer_code",
            "name",
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "trn",
            "email",
            "phone",
            "status",
            "default_payment_terms_days",
            "retention_rate",
            "late_fee_rate",
            "notes",
            "contacts",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CustomerCreateSerializer(serializers.ModelSerializer):
    contacts = CustomerContactSerializer(many=True, required=False)

    class Meta:
        model = Customer
        fields = (
            "customer_code",
            "name",
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "trn",
            "email",
            "phone",
            "status",
            "default_payment_terms_days",
            "retention_rate",
            "late_fee_rate",
            "notes",
            "contacts",
        )

    def create(self, validated_data):
        from apps.customers.services.customer import CustomerService

        tenant = self.context["request"].user.tenant
        return CustomerService.create_customer(tenant=tenant, **validated_data)


class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "customer_code",
            "name",
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "trn",
            "email",
            "phone",
            "status",
            "default_payment_terms_days",
            "retention_rate",
            "late_fee_rate",
            "notes",
        )
