from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins.pdf_action import PDFExportMixin
from apps.core.permissions import IsTenantMember
from apps.warranty_certificates.models import WarrantyCertificate
from apps.warranty_certificates.serializers import (
    WarrantyCertificateDetailSerializer,
    WarrantyCertificateListSerializer,
    WarrantyCertificateWriteSerializer,
)
from apps.warranty_certificates.services.warranty_certificate import WarrantyCertificateService


@extend_schema_view(
    list=extend_schema(tags=["Warranty Certificates"]),
    create=extend_schema(tags=["Warranty Certificates"]),
    retrieve=extend_schema(tags=["Warranty Certificates"]),
    update=extend_schema(tags=["Warranty Certificates"]),
    partial_update=extend_schema(tags=["Warranty Certificates"]),
    destroy=extend_schema(tags=["Warranty Certificates"]),
)
class WarrantyCertificateViewSet(PDFExportMixin, viewsets.ModelViewSet):
    pdf_document_type = "warranty_certificate"
    permission_classes = [IsTenantMember]
    search_fields = [
        "reference_number",
        "customer__name",
        "project_name",
        "customer_lpo",
        "service_report_reference",
        "items__product_name",
        "items__specification",
        "items__identifier",
    ]
    ordering_fields = ["certificate_date", "reference_number", "warranty_end_date"]
    ordering = ["-certificate_date"]

    def get_queryset(self):
        return WarrantyCertificate.objects.filter(
            tenant=self.request.user.tenant
        ).select_related("customer", "entity", "service_report").prefetch_related("items")

    def get_serializer_class(self):
        if self.action == "list":
            return WarrantyCertificateListSerializer
        if self.action in ("create", "update", "partial_update"):
            return WarrantyCertificateWriteSerializer
        return WarrantyCertificateDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        certificate = serializer.save()
        output = WarrantyCertificateDetailSerializer(certificate, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        certificate = serializer.save()
        output = WarrantyCertificateDetailSerializer(certificate, context={"request": request})
        return Response(output.data)

    @extend_schema(tags=["Warranty Certificates"])
    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        certificate = self.get_object()
        try:
            certificate = WarrantyCertificateService.issue(certificate)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WarrantyCertificateDetailSerializer(certificate).data)
