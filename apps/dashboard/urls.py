from django.urls import path

from apps.dashboard.views.dashboard import DashboardView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]
