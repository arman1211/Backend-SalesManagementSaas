from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins.pdf_action import PDFExportMixin
from apps.core.permissions import IsTenantMember
from apps.credit_notes.models import CreditNote
from apps.credit_notes.serializers import (
    CreditNoteDetailSerializer,
    CreditNoteListSerializer,
    CreditNoteWriteSerializer,
)
from apps.credit_notes.services.credit_note import CreditNoteService


@extend_schema_view(
    list=extend_schema(tags=["Credit Notes"]),
    create=extend_schema(tags=["Credit Notes"]),
    retrieve=extend_schema(tags=["Credit Notes"]),
    update=extend_schema(tags=["Credit Notes"]),
    partial_update=extend_schema(tags=["Credit Notes"]),
    destroy=extend_schema(tags=["Credit Notes"]),
)
class CreditNoteViewSet(PDFExportMixin, viewsets.ModelViewSet):
    pdf_document_type = "credit_note"
    permission_classes = [IsTenantMember]
    search_fields = ["credit_note_number", "customer__name", "original_invoice__invoice_number"]
    ordering_fields = ["credit_note_date", "credit_note_number", "grand_total"]
    ordering = ["-credit_note_date"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return CreditNote.objects.filter(
            tenant=self.request.user.tenant
        ).select_related("customer", "entity", "original_invoice").prefetch_related("line_items")

    def get_serializer_class(self):
        if self.action == "list":
            return CreditNoteListSerializer
        if self.action == "create":
            return CreditNoteWriteSerializer
        return CreditNoteDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credit_note = serializer.save()
        output = CreditNoteDetailSerializer(credit_note, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Credit Notes"])
    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        credit_note = self.get_object()
        credit_note = CreditNoteService.issue(credit_note)
        return Response(CreditNoteDetailSerializer(credit_note).data)
