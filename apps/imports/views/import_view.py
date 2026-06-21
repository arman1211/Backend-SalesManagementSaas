from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsTenantMember
from apps.imports.services.import_service import ImportService


class ImportPreviewView(APIView):
    permission_classes = [IsTenantMember]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(tags=["Imports"])
    def post(self, request):
        uploaded_file = request.FILES.get("file")
        import_type = request.data.get("type")
        if not uploaded_file:
            return Response({"detail": "Excel file is required."}, status=400)
        if import_type not in ("customers", "payments"):
            return Response({"detail": "type must be customers or payments."}, status=400)
        sheet_name = request.data.get("sheet") or None
        result = ImportService.preview(uploaded_file, import_type, sheet_name)
        return Response(result)


class ImportExecuteView(APIView):
    permission_classes = [IsTenantMember]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(tags=["Imports"])
    def post(self, request):
        uploaded_file = request.FILES.get("file")
        import_type = request.data.get("type")
        if not uploaded_file:
            return Response({"detail": "Excel file is required."}, status=400)
        if import_type not in ("customers", "payments"):
            return Response({"detail": "type must be customers or payments."}, status=400)
        sheet_name = request.data.get("sheet") or None
        result = ImportService.execute(
            tenant=request.user.tenant,
            user=request.user,
            uploaded_file=uploaded_file,
            import_type=import_type,
            sheet_name=sheet_name,
        )
        return Response(result, status=status.HTTP_201_CREATED)
