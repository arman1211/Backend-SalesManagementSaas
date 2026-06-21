from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsTenantMember
from apps.dashboard.services.dashboard import DashboardService


@extend_schema(tags=["Dashboard"])
class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        data = DashboardService.get_summary(request.user.tenant)
        return Response(data)
