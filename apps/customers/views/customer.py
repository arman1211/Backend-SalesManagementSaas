from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsTenantMember
from apps.customers.models import Customer
from apps.customers.serializers import (
    CustomerCreateSerializer,
    CustomerDetailSerializer,
    CustomerListSerializer,
    CustomerUpdateSerializer,
)
from apps.customers.services import CustomerService


@extend_schema_view(
    list=extend_schema(tags=["Customers"]),
    create=extend_schema(tags=["Customers"]),
    retrieve=extend_schema(tags=["Customers"]),
    update=extend_schema(tags=["Customers"]),
    partial_update=extend_schema(tags=["Customers"]),
    destroy=extend_schema(tags=["Customers"]),
)
class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantMember]
    search_fields = ["name", "customer_code", "trn", "email", "phone"]
    ordering_fields = ["name", "customer_code", "created_at", "status"]
    ordering = ["name"]

    def get_queryset(self):
        return CustomerService.get_tenant_customers(self.request.user.tenant)

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        if self.action == "create":
            return CustomerCreateSerializer
        if self.action in ("update", "partial_update"):
            return CustomerUpdateSerializer
        return CustomerDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        output = CustomerDetailSerializer(customer, context={"request": request})
        return Response(output.data, status=201)

    def perform_destroy(self, instance):
        instance.status = Customer.Status.INACTIVE
        instance.save(update_fields=["status", "updated_at"])

    @extend_schema(tags=["Customers"])
    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        customer = self.get_object()
        from apps.credit_notes.models import CreditNote
        from apps.invoices.models import Invoice
        from apps.payments.models import Payment
        from apps.reports.services.report import ReportService

        statement = ReportService.account_statement(
            tenant=request.user.tenant,
            customer_id=str(customer.id),
        )

        invoices = Invoice.objects.filter(
            tenant=request.user.tenant, customer=customer
        ).exclude(status=Invoice.Status.CANCELLED).order_by("-invoice_date")[:20]
        quotations = customer.quotations.order_by("-quotation_date")[:20]
        service_reports = customer.service_reports.order_by("-report_date")[:20]
        credit_notes = CreditNote.objects.filter(
            tenant=request.user.tenant, customer=customer
        ).order_by("-credit_note_date")[:20]
        payments = Payment.objects.filter(
            tenant=request.user.tenant, customer=customer
        ).select_related("invoice").order_by("-payment_date")[:20]

        from decimal import Decimal

        unpaid_balance = sum(
            (inv.net_amount_due for inv in Invoice.objects.filter(
                tenant=request.user.tenant,
                customer=customer,
                payment_status=Invoice.PaymentStatus.UNPAID,
            ).exclude(status=Invoice.Status.CANCELLED)),
            Decimal("0.00"),
        )

        return Response({
            "customer": CustomerDetailSerializer(customer, context={"request": request}).data,
            "account_summary": statement["summary"],
            "outstanding_balance": str(unpaid_balance),
            "transactions": statement["transactions"],
            "quotations": list(quotations.values(
                "id", "reference_number", "quotation_date", "grand_total", "status"
            )),
            "invoices": list(invoices.values(
                "id", "invoice_number", "invoice_date", "grand_total",
                "balance_amount", "payment_status", "status", "exceed_days",
            )),
            "service_reports": list(service_reports.values(
                "id", "reference_number", "report_date", "status", "job_status"
            )),
            "credit_notes": list(credit_notes.values(
                "id", "credit_note_number", "credit_note_date", "grand_total", "status"
            )),
            "payments": [
                {
                    "id": str(pay.id),
                    "payment_date": pay.payment_date.isoformat(),
                    "amount": str(pay.amount),
                    "payment_method": pay.payment_method,
                    "invoice_id": str(pay.invoice_id),
                    "invoice_number": pay.invoice.invoice_number,
                }
                for pay in payments
            ],
        })
