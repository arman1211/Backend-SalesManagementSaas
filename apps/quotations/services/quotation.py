from datetime import timedelta

from django.utils import timezone

from apps.core.services.calculations import calculate_document_totals
from apps.core.services.documents import apply_totals_to_document, sync_line_items
from apps.core.services.numbering import get_next_sequence
from apps.invoices.models import Invoice, InvoiceLineItem
from apps.invoices.services.receivable import refresh_invoice_receivable
from apps.quotations.models import Quotation, QuotationLineItem


class QuotationService:
    @staticmethod
    def _assign_reference(quotation):
        if not quotation.reference_number:
            seq = get_next_sequence(quotation.entity, "next_quotation_number")
            quotation.reference_number = f"{quotation.entity.quotation_prefix}-{seq}"

    @staticmethod
    def create(tenant, user, entity, customer, line_items, **data):
        quotation = Quotation.objects.create(
            tenant=tenant,
            entity=entity,
            customer=customer,
            created_by=user,
            **data,
        )
        QuotationService._assign_reference(quotation)
        sync_line_items(quotation, line_items, QuotationLineItem, "quotation")
        apply_totals_to_document(quotation, quotation.line_items.all())
        if quotation.validity_days and not quotation.valid_until:
            quotation.valid_until = quotation.quotation_date + timedelta(
                days=quotation.validity_days
            )
        quotation.save()
        return quotation

    @staticmethod
    def update(quotation, line_items=None, **data):
        for field, value in data.items():
            setattr(quotation, field, value)
        if line_items is not None:
            sync_line_items(quotation, line_items, QuotationLineItem, "quotation")
        apply_totals_to_document(quotation, quotation.line_items.all())
        if quotation.validity_days and quotation.quotation_date:
            quotation.valid_until = quotation.quotation_date + timedelta(
                days=quotation.validity_days
            )
        quotation.save()
        return quotation

    @staticmethod
    def convert_to_invoice(quotation, user, **invoice_data):
        from apps.invoices.services.invoice import InvoiceService

        line_items = [
            {
                "description": item.description,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "serial_number": item.serial_number,
            }
            for item in quotation.line_items.all()
        ]
        invoice = InvoiceService.create(
            tenant=quotation.tenant,
            user=user,
            entity=quotation.entity,
            customer=quotation.customer,
            line_items=line_items,
            quotation=quotation,
            quotation_reference=quotation.reference_number,
            customer_lpo=quotation.customer_lpo or invoice_data.get("customer_lpo", ""),
            discount_amount=quotation.discount_amount,
            discount_percent=quotation.discount_percent,
            vat_rate=quotation.vat_rate,
            payment_terms_days=quotation.payment_terms_days,
            **invoice_data,
        )
        quotation.status = Quotation.Status.CONVERTED
        quotation.save(update_fields=["status", "updated_at"])
        return invoice
