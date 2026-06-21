from apps.core.services.calculations import calculate_document_totals
from apps.core.services.documents import apply_totals_to_document, sync_line_items
from apps.core.services.numbering import get_next_sequence
from apps.invoices.models import Invoice, InvoiceLineItem
from apps.invoices.services.receivable import refresh_invoice_receivable


class InvoiceService:
    @staticmethod
    def create(tenant, user, entity, customer, line_items, **data):
        invoice_number = data.pop("invoice_number", None) or get_next_sequence(
            entity, "next_invoice_number"
        )
        invoice = Invoice.objects.create(
            tenant=tenant,
            entity=entity,
            customer=customer,
            invoice_number=invoice_number,
            created_by=user,
            **data,
        )
        sync_line_items(invoice, line_items, InvoiceLineItem, "invoice")
        apply_totals_to_document(invoice, invoice.line_items.all())

        if not invoice.retention_rate:
            invoice.retention_rate = tenant.default_retention_rate
        if not invoice.late_fee_rate:
            invoice.late_fee_rate = tenant.default_late_fee_rate
        if not invoice.payment_terms_days:
            invoice.payment_terms_days = tenant.default_payment_terms_days

        invoice.save()
        if invoice.status != Invoice.Status.DRAFT:
            refresh_invoice_receivable(invoice)
        return invoice

    @staticmethod
    def update(invoice, line_items=None, **data):
        for field, value in data.items():
            setattr(invoice, field, value)
        if line_items is not None:
            sync_line_items(invoice, line_items, InvoiceLineItem, "invoice")
        apply_totals_to_document(invoice, invoice.line_items.all())
        invoice.save()
        if invoice.status != Invoice.Status.DRAFT:
            refresh_invoice_receivable(invoice)
        return invoice

    @staticmethod
    def finalize(invoice):
        invoice.status = Invoice.Status.ISSUED
        invoice.save(update_fields=["status", "updated_at"])
        refresh_invoice_receivable(invoice)
        return invoice

    @staticmethod
    def create_from_quotation(quotation, user, **data):
        from apps.quotations.services.quotation import QuotationService

        return QuotationService.convert_to_invoice(quotation, user, **data)
