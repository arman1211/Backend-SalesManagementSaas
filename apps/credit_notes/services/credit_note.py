from apps.core.services.documents import apply_totals_to_document, sync_line_items
from apps.core.services.numbering import get_next_sequence
from apps.credit_notes.models import CreditNote, CreditNoteLineItem


class CreditNoteService:
    @staticmethod
    def create(tenant, user, entity, customer, original_invoice, line_items, **data):
        credit_note_number = data.pop("credit_note_number", None) or get_next_sequence(
            entity, "next_credit_note_number"
        )
        credit_note = CreditNote.objects.create(
            tenant=tenant,
            entity=entity,
            customer=customer,
            original_invoice=original_invoice,
            credit_note_number=credit_note_number,
            created_by=user,
            customer_lpo=original_invoice.customer_lpo,
            site_reference=data.get("site_reference", ""),
            vat_rate=original_invoice.vat_rate,
            **data,
        )
        sync_line_items(credit_note, line_items, CreditNoteLineItem, "credit_note")
        totals = apply_totals_to_document(credit_note, credit_note.line_items.all())
        credit_note.save()
        return credit_note

    @staticmethod
    def create_from_invoice(invoice, user, line_items=None, **data):
        if line_items is None:
            line_items = [
                {
                    "description": item.description,
                    "unit_price": item.unit_price,
                    "quantity": item.quantity,
                    "serial_number": item.serial_number,
                }
                for item in invoice.line_items.all()
            ]
        credit_note = CreditNoteService.create(
            tenant=invoice.tenant,
            user=user,
            entity=invoice.entity,
            customer=invoice.customer,
            original_invoice=invoice,
            line_items=line_items,
            **data,
        )
        from apps.invoices.services.receivable import refresh_invoice_receivable

        refresh_invoice_receivable(invoice)
        return credit_note

    @staticmethod
    def issue(credit_note):
        credit_note.status = CreditNote.Status.ISSUED
        credit_note.save(update_fields=["status", "updated_at"])
        from apps.invoices.services.receivable import refresh_invoice_receivable

        refresh_invoice_receivable(credit_note.original_invoice)
        return credit_note
