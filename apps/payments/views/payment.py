from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.core.permissions import IsTenantMember
from apps.payments.models import Payment
from apps.payments.serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentWriteSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Payments"]),
    create=extend_schema(tags=["Payments"]),
    retrieve=extend_schema(tags=["Payments"]),
)
class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantMember]
    search_fields = ["reference_number", "customer__name", "invoice__invoice_number"]
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = Payment.objects.filter(tenant=self.request.user.tenant).select_related(
            "customer", "invoice"
        )
        customer_id = self.request.query_params.get("customer")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        invoice_id = self.request.query_params.get("invoice")
        if invoice_id:
            qs = qs.filter(invoice_id=invoice_id)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentWriteSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentListSerializer
