from django.urls import include, path

from apps.tenants.views.entity import CompanyEntityViewSet
from apps.tenants.views.tenant import TenantDetailView
from rest_framework.routers import DefaultRouter

app_name = "tenants"

entity_router = DefaultRouter()
entity_router.register("entities", CompanyEntityViewSet, basename="entity")

urlpatterns = [
    path("me/", TenantDetailView.as_view(), name="tenant-detail"),
    path("", include(entity_router.urls)),
]
