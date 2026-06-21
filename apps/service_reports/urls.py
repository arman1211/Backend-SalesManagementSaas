from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.service_reports.views.service_report import ServiceReportViewSet

app_name = "service_reports"

router = DefaultRouter()
router.register("", ServiceReportViewSet, basename="service-report")

urlpatterns = [path("", include(router.urls))]
