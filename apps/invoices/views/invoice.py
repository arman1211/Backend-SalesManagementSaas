from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins.pdf_action import PDFExportMixin
from apps.core.permissions import IsTenantMember
from apps.invoices.models import Invoice
from apps.invoices.serializers import (
    InvoiceDetailSerializer,
    InvoiceListSerializer,
    InvoiceWriteSerializer,
)
from apps.invoices.services.invoice import InvoiceService
from apps.invoices.services.receivable import refresh_invoice_receivable


@extend_schema_view(
    list=extend_schema(tags=["Invoices"]),
    create=extend_schema(tags=["Invoices"]),
    retrieve=extend_schema(tags=["Invoices"]),
    update=extend_schema(tags=["Invoices"]),
    partial_update=extend_schema(tags=["Invoices"]),
    destroy=extend_schema(tags=["Invoices"]),
)
class InvoiceViewSet(PDFExportMixin, viewsets.ModelViewSet):
    pdf_document_type = "invoice"
    permission_classes = [IsTenantMember]
    search_fields = ["invoice_number", "customer__name", "customer_lpo", "drn"]
    ordering_fields = ["invoice_date", "invoice_number", "grand_total", "payment_status"]
    ordering = ["-invoice_date"]

    def get_queryset(self):
        qs = Invoice.objects.filter(tenant=self.request.user.tenant).select_related(
            "customer", "entity"
        ).prefetch_related("line_items", "payments")

        payment_status = self.request.query_params.get("payment_status")
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        customer_id = self.request.query_params.get("customer")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        if self.action in ("create", "update", "partial_update"):
            return InvoiceWriteSerializer
        return InvoiceDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        output = InvoiceDetailSerializer(invoice, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        output = InvoiceDetailSerializer(invoice, context={"request": request})
        return Response(output.data)

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        invoice.status = Invoice.Status.CANCELLED
        invoice.save(update_fields=["status", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["Invoices"])
    @action(detail=True, methods=["post"])
    def finalize(self, request, pk=None):
        invoice = self.get_object()
        invoice = InvoiceService.finalize(invoice)
        return Response(InvoiceDetailSerializer(invoice).data)

    @extend_schema(tags=["Invoices"])
    @action(detail=True, methods=["post"], url_path="refresh-receivable")
    def refresh_receivable(self, request, pk=None):
        invoice = self.get_object()
        invoice = refresh_invoice_receivable(invoice)
        return Response(InvoiceDetailSerializer(invoice).data)

    @extend_schema(tags=["Invoices"])
    @action(detail=False, methods=["get"], url_path="outstanding")
    def outstanding(self, request):
        qs = self.get_queryset().filter(payment_status=Invoice.PaymentStatus.UNPAID)
        page = self.paginate_queryset(qs)
        serializer = InvoiceListSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @extend_schema(tags=["Invoices"])
    @action(detail=False, methods=["get"])
    def overdue(self, request):
        qs = self.get_queryset().filter(status=Invoice.Status.OVERDUE)
        page = self.paginate_queryset(qs)
        serializer = InvoiceListSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
