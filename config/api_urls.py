from django.urls import include, path

urlpatterns = [
    path("health/", include("apps.core.urls")),
    path("auth/", include("apps.accounts.urls")),
    path("tenants/", include("apps.tenants.urls")),
    path("customers/", include("apps.customers.urls")),
    path("quotations/", include("apps.quotations.urls")),
    path("invoices/", include("apps.invoices.urls")),
    path("service-reports/", include("apps.service_reports.urls")),
    path("credit-notes/", include("apps.credit_notes.urls")),
    path("payments/", include("apps.payments.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("reports/", include("apps.reports.urls")),
    path("imports/", include("apps.imports.urls")),
]
