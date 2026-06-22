from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.warranty_certificates.views.warranty_certificate import WarrantyCertificateViewSet

app_name = "warranty_certificates"

router = DefaultRouter()
router.register("", WarrantyCertificateViewSet, basename="warranty-certificate")

urlpatterns = [path("", include(router.urls))]
