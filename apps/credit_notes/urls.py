from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.credit_notes.views.credit_note import CreditNoteViewSet

app_name = "credit_notes"

router = DefaultRouter()
router.register("", CreditNoteViewSet, basename="credit-note")

urlpatterns = [path("", include(router.urls))]
