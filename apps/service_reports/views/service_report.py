from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins.pdf_action import PDFExportMixin
from apps.core.permissions import IsTenantMember
from apps.service_reports.models import ServiceReport
from apps.service_reports.serializers import (
    ServiceReportDetailSerializer,
    ServiceReportListSerializer,
    ServiceReportWriteSerializer,
)
from apps.service_reports.services.service_report import ServiceReportService


@extend_schema_view(
    list=extend_schema(tags=["Service Reports"]),
    create=extend_schema(tags=["Service Reports"]),
    retrieve=extend_schema(tags=["Service Reports"]),
    update=extend_schema(tags=["Service Reports"]),
    partial_update=extend_schema(tags=["Service Reports"]),
    destroy=extend_schema(tags=["Service Reports"]),
)
class ServiceReportViewSet(PDFExportMixin, viewsets.ModelViewSet):
    pdf_document_type = "service_report"
    permission_classes = [IsTenantMember]
    search_fields = ["reference_number", "customer__name", "drn", "customer_lpo"]
    ordering_fields = ["report_date", "reference_number", "status"]
    ordering = ["-report_date"]

    def get_queryset(self):
        return ServiceReport.objects.filter(
            tenant=self.request.user.tenant
        ).select_related("customer", "entity")

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceReportListSerializer
        if self.action in ("create", "update", "partial_update"):
            return ServiceReportWriteSerializer
        return ServiceReportDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        output = ServiceReportDetailSerializer(report, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        output = ServiceReportDetailSerializer(report, context={"request": request})
        return Response(output.data)

    @extend_schema(tags=["Service Reports"])
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        report = self.get_object()
        report = ServiceReportService.complete(report)
        return Response(ServiceReportDetailSerializer(report).data)
