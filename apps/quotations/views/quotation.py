from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins.pdf_action import PDFExportMixin
from apps.core.permissions import IsTenantMember
from apps.quotations.models import Quotation
from apps.quotations.serializers import (
    QuotationDetailSerializer,
    QuotationListSerializer,
    QuotationWriteSerializer,
)
from apps.quotations.services.quotation import QuotationService


@extend_schema_view(
    list=extend_schema(tags=["Quotations"]),
    create=extend_schema(tags=["Quotations"]),
    retrieve=extend_schema(tags=["Quotations"]),
    update=extend_schema(tags=["Quotations"]),
    partial_update=extend_schema(tags=["Quotations"]),
    destroy=extend_schema(tags=["Quotations"]),
)
class QuotationViewSet(PDFExportMixin, viewsets.ModelViewSet):
    pdf_document_type = "quotation"
    permission_classes = [IsTenantMember]
    search_fields = ["reference_number", "customer__name", "customer_lpo"]
    ordering_fields = ["quotation_date", "reference_number", "grand_total", "status"]
    ordering = ["-quotation_date"]

    def get_queryset(self):
        return Quotation.objects.filter(
            tenant=self.request.user.tenant
        ).select_related("customer", "entity").prefetch_related("line_items")

    def get_serializer_class(self):
        if self.action == "list":
            return QuotationListSerializer
        if self.action in ("create", "update", "partial_update"):
            return QuotationWriteSerializer
        return QuotationDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quotation = serializer.save()
        output = QuotationDetailSerializer(quotation, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        quotation = serializer.save()
        output = QuotationDetailSerializer(quotation, context={"request": request})
        return Response(output.data)

    @extend_schema(tags=["Quotations"])
    @action(detail=True, methods=["post"], url_path="convert-to-invoice")
    def convert_to_invoice(self, request, pk=None):
        quotation = self.get_object()
        invoice = QuotationService.convert_to_invoice(quotation, request.user)
        from apps.invoices.serializers import InvoiceDetailSerializer

        return Response(
            InvoiceDetailSerializer(invoice, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
