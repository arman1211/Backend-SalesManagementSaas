from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.quotations.views.quotation import QuotationViewSet

app_name = "quotations"

router = DefaultRouter()
router.register("", QuotationViewSet, basename="quotation")

urlpatterns = [path("", include(router.urls))]
