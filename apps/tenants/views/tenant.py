from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsTenantMember
from apps.tenants.models import Tenant
from apps.tenants.serializers import TenantSerializer


class TenantDetailView(RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's tenant."""

    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get_object(self):
        return self.request.user.tenant
