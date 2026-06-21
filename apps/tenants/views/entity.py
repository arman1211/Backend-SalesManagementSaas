from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.core.permissions import IsTenantMember
from apps.tenants.models import CompanyEntity
from apps.tenants.serializers import CompanyEntitySerializer


@extend_schema_view(
    list=extend_schema(tags=["Entities"]),
    create=extend_schema(tags=["Entities"]),
    retrieve=extend_schema(tags=["Entities"]),
    update=extend_schema(tags=["Entities"]),
    partial_update=extend_schema(tags=["Entities"]),
    destroy=extend_schema(tags=["Entities"]),
)
class CompanyEntityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantMember]
    serializer_class = CompanyEntitySerializer
    search_fields = ["name", "trn"]
    ordering = ["name"]

    def get_queryset(self):
        return CompanyEntity.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)
