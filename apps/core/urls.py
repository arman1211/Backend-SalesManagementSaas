from django.http import JsonResponse
from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@extend_schema(tags=["Health"])
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "ok", "service": "sales-management-api"})


urlpatterns = [
    path("", health_check, name="health-check"),
]
