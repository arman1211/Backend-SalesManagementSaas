from apps.core.services.numbering import get_next_sequence
from apps.invoices.services.receivable import refresh_invoice_receivable
from apps.payments.models import Payment


class PaymentService:
    @staticmethod
    def record_payment(tenant, user, invoice, **data):
        payment = Payment.objects.create(
            tenant=tenant,
            customer=invoice.customer,
            invoice=invoice,
            recorded_by=user,
            **data,
        )
        refresh_invoice_receivable(invoice)
        return payment
