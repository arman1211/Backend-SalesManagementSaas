from django.urls import path

from apps.reports.views.report import (
    AccountStatementView,
    AgingReportView,
    CollectionsReportView,
    SalesSummaryView,
    VATSummaryView,
)

app_name = "reports"

urlpatterns = [
    path("aging/", AgingReportView.as_view(), name="aging"),
    path("account-statement/", AccountStatementView.as_view(), name="account-statement"),
    path("vat-summary/", VATSummaryView.as_view(), name="vat-summary"),
    path("collections/", CollectionsReportView.as_view(), name="collections"),
    path("sales-summary/", SalesSummaryView.as_view(), name="sales-summary"),
]
