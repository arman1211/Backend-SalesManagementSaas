from datetime import datetime

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsTenantMember
from apps.reports.services.report import ReportService


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@extend_schema(tags=["Reports"])
class AgingReportView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        return Response(ReportService.aging_report(request.user.tenant))


@extend_schema(tags=["Reports"])
class AccountStatementView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="customer", required=True, type=str),
            OpenApiParameter(name="from_date", required=False, type=str),
            OpenApiParameter(name="to_date", required=False, type=str),
        ]
    )
    def get(self, request):
        customer_id = request.query_params.get("customer")
        if not customer_id:
            return Response({"detail": "customer query param is required."}, status=400)
        data = ReportService.account_statement(
            tenant=request.user.tenant,
            customer_id=customer_id,
            from_date=parse_date(request.query_params.get("from_date")),
            to_date=parse_date(request.query_params.get("to_date")),
        )
        return Response(data)


@extend_schema(tags=["Reports"])
class VATSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="from_date", required=False, type=str),
            OpenApiParameter(name="to_date", required=False, type=str),
        ]
    )
    def get(self, request):
        return Response(
            ReportService.vat_summary(
                tenant=request.user.tenant,
                from_date=parse_date(request.query_params.get("from_date")),
                to_date=parse_date(request.query_params.get("to_date")),
            )
        )


@extend_schema(tags=["Reports"])
class CollectionsReportView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="from_date", required=False, type=str),
            OpenApiParameter(name="to_date", required=False, type=str),
        ]
    )
    def get(self, request):
        return Response(
            ReportService.collections_report(
                tenant=request.user.tenant,
                from_date=parse_date(request.query_params.get("from_date")),
                to_date=parse_date(request.query_params.get("to_date")),
            )
        )


@extend_schema(tags=["Reports"])
class SalesSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="from_date", required=False, type=str),
            OpenApiParameter(name="to_date", required=False, type=str),
        ]
    )
    def get(self, request):
        return Response(
            ReportService.sales_summary(
                tenant=request.user.tenant,
                from_date=parse_date(request.query_params.get("from_date")),
                to_date=parse_date(request.query_params.get("to_date")),
            )
        )
