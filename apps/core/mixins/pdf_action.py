from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from apps.core.services.pdf import DocumentPDFService


class PDFExportMixin:
    pdf_document_type: str = ""

    @extend_schema(tags=["Documents"])
    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        instance = self.get_object()
        content, filename = DocumentPDFService.generate(
            self.pdf_document_type,
            instance,
            request.user.tenant,
        )
        response = HttpResponse(content, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
