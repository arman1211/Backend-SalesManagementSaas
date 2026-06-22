import base64
import mimetypes
from decimal import Decimal
from io import BytesIO

from django.template.loader import render_to_string
from xhtml2pdf import pisa


def _format_money(value):
    if value is None:
        return "0.00"
    return f"{Decimal(str(value)):,.2f}"


def _format_date(value):
    if not value:
        return ""
    return value.strftime("%d/%m/%Y")


def _image_to_data_uri(image_field):
    if not image_field:
        return None
    try:
        mime, _ = mimetypes.guess_type(image_field.name)
        with image_field.open("rb") as handle:
            encoded = base64.b64encode(handle.read()).decode("ascii")
        return f"data:{mime or 'image/png'};base64,{encoded}"
    except (OSError, ValueError):
        return None


def _entity_context(entity, tenant):
    logo = _image_to_data_uri(entity.logo) if entity and entity.logo else None
    if not logo and tenant and tenant.logo:
        logo = _image_to_data_uri(tenant.logo)
    source = entity or tenant
    return {
        "company_name": getattr(source, "legal_name", "") or getattr(source, "name", ""),
        "trade_name": getattr(source, "name", ""),
        "trn": getattr(source, "trn", ""),
        "email": getattr(source, "email", ""),
        "phone": getattr(source, "phone", ""),
        "address_line_1": getattr(source, "address_line_1", ""),
        "address_line_2": getattr(source, "address_line_2", ""),
        "city": getattr(source, "city", ""),
        "country": getattr(source, "country", ""),
        "logo_data_uri": logo,
        "bank_name": tenant.bank_name if tenant else "",
        "bank_account_name": tenant.bank_account_name if tenant else "",
        "bank_account_number": tenant.bank_account_number if tenant else "",
        "bank_iban": tenant.bank_iban if tenant else "",
    }


def _customer_context(customer):
    return {
        "name": customer.name,
        "trn": customer.trn,
        "address_line_1": customer.address_line_1,
        "address_line_2": customer.address_line_2,
        "city": customer.city,
        "country": customer.country,
        "phone": customer.phone,
        "email": customer.email,
    }


def _line_items_context(items):
    rows = []
    for item in items:
        rows.append({
            "serial_number": item.serial_number,
            "description": item.description,
            "unit_price": _format_money(item.unit_price),
            "quantity": item.quantity,
            "line_total": _format_money(item.line_total),
        })
    return rows


class DocumentPDFService:
    TEMPLATES = {
        "invoice": "pdf/invoice.html",
        "quotation": "pdf/quotation.html",
        "service_report": "pdf/service_report.html",
        "credit_note": "pdf/credit_note.html",
        "warranty_certificate": "pdf/warranty_certificate.html",
    }

    @classmethod
    def generate(cls, document_type, instance, tenant):
        builder = getattr(cls, f"_context_{document_type}")
        context = builder(instance, tenant)
        context["format_money"] = _format_money
        html = render_to_string(cls.TEMPLATES[document_type], context)
        buffer = BytesIO()
        pdf = pisa.CreatePDF(html, dest=buffer)
        if pdf.err:
            raise ValueError("Failed to generate PDF")
        filename = context.get("filename", f"{document_type}.pdf")
        return buffer.getvalue(), filename

    @staticmethod
    def _context_invoice(invoice, tenant):
        entity = invoice.entity
        return {
            "filename": f"Tax-Invoice-{invoice.invoice_number}.pdf",
            "title": "Tax Invoice",
            "entity": _entity_context(entity, tenant),
            "customer": _customer_context(invoice.customer),
            "header_meta_rows": [
                {"label": "Invoice No.", "value": str(invoice.invoice_number)},
                {"label": "Invoice Date", "value": _format_date(invoice.invoice_date)},
                {"label": "Due Date", "value": _format_date(invoice.due_date)},
            ],
            "document_number": str(invoice.invoice_number),
            "document_date": _format_date(invoice.invoice_date),
            "due_date": _format_date(invoice.due_date),
            "customer_lpo": invoice.customer_lpo,
            "drn": invoice.drn,
            "quotation_reference": invoice.quotation_reference,
            "payment_terms_days": invoice.payment_terms_days,
            "payment_terms_text": invoice.payment_terms_text or tenant.default_payment_terms_text,
            "payment_status": invoice.payment_status,
            "exceed_days": invoice.exceed_days,
            "line_items": _line_items_context(invoice.line_items.all()),
            "subtotal": _format_money(invoice.subtotal),
            "discount_amount": _format_money(invoice.discount_amount),
            "net_total": _format_money(invoice.net_total),
            "vat_rate_percent": f"{Decimal(str(invoice.vat_rate)) * 100:.0f}",
            "vat_amount": _format_money(invoice.vat_amount),
            "grand_total": _format_money(invoice.grand_total),
            "retention_amount": _format_money(invoice.retention_amount),
            "amount_received": _format_money(invoice.amount_received),
            "balance_amount": _format_money(invoice.balance_amount),
            "net_amount_due": _format_money(invoice.net_amount_due),
            "notes": invoice.notes,
        }

    @staticmethod
    def _context_quotation(quotation, tenant):
        entity = quotation.entity
        return {
            "filename": f"Quotation-{quotation.reference_number}.pdf",
            "title": "Quotation",
            "entity": _entity_context(entity, tenant),
            "customer": _customer_context(quotation.customer),
            "header_meta_rows": [
                {"label": "Reference", "value": quotation.reference_number},
                {"label": "Date", "value": _format_date(quotation.quotation_date)},
                {"label": "Valid Until", "value": _format_date(quotation.valid_until)},
            ],
            "document_number": quotation.reference_number,
            "document_date": _format_date(quotation.quotation_date),
            "valid_until": _format_date(quotation.valid_until),
            "attention_person": quotation.attention_person,
            "customer_lpo": quotation.customer_lpo,
            "site_reference": quotation.site_reference,
            "payment_terms_days": quotation.payment_terms_days,
            "payment_terms_text": quotation.payment_terms_text or tenant.default_payment_terms_text,
            "terms_and_conditions": quotation.terms_and_conditions or tenant.default_terms_and_conditions,
            "line_items": _line_items_context(quotation.line_items.all()),
            "subtotal": _format_money(quotation.subtotal),
            "discount_amount": _format_money(quotation.discount_amount),
            "net_total": _format_money(quotation.net_total),
            "vat_rate_percent": f"{Decimal(str(quotation.vat_rate)) * 100:.0f}",
            "vat_amount": _format_money(quotation.vat_amount),
            "grand_total": _format_money(quotation.grand_total),
            "notes": quotation.notes,
        }

    @staticmethod
    def _context_service_report(report, tenant):
        entity = report.entity
        return {
            "filename": f"Service-Report-{report.reference_number}.pdf",
            "title": "Work Completion Report",
            "entity": _entity_context(entity, tenant),
            "customer": _customer_context(report.customer),
            "header_meta_rows": [
                {"label": "Reference", "value": report.reference_number},
                {"label": "Report Date", "value": _format_date(report.report_date)},
                {"label": "Status", "value": report.get_job_status_display()},
            ],
            "document_number": report.reference_number,
            "document_date": _format_date(report.report_date),
            "attention_person": report.attention_person,
            "customer_lpo": report.customer_lpo,
            "drn": report.drn,
            "quotation_reference": report.quotation_reference,
            "equipment_details": report.equipment_details,
            "equipment_id": report.equipment_id,
            "site_location": report.site_location,
            "work_description": report.work_description,
            "work_start_date": _format_date(report.work_start_date),
            "completion_date": _format_date(report.completion_date),
            "recommendations": report.recommendations,
            "job_status": report.get_job_status_display(),
            "technician_name": report.technician_name,
            "notes": report.notes,
        }

    @staticmethod
    def _context_credit_note(credit_note, tenant):
        entity = credit_note.entity
        return {
            "filename": f"Credit-Note-{credit_note.credit_note_number}.pdf",
            "title": "Tax Credit Note",
            "entity": _entity_context(entity, tenant),
            "customer": _customer_context(credit_note.customer),
            "header_meta_rows": [
                {"label": "Credit Note No.", "value": str(credit_note.credit_note_number)},
                {"label": "Date", "value": _format_date(credit_note.credit_note_date)},
                {"label": "Original Invoice", "value": str(credit_note.original_invoice.invoice_number)},
            ],
            "document_number": str(credit_note.credit_note_number),
            "document_date": _format_date(credit_note.credit_note_date),
            "original_invoice_number": str(credit_note.original_invoice.invoice_number),
            "customer_lpo": credit_note.customer_lpo,
            "site_reference": credit_note.site_reference,
            "reason": credit_note.reason,
            "line_items": _line_items_context(credit_note.line_items.all()),
            "subtotal": _format_money(credit_note.subtotal),
            "vat_rate_percent": f"{Decimal(str(credit_note.vat_rate)) * 100:.0f}",
            "vat_amount": _format_money(credit_note.vat_amount),
            "grand_total": _format_money(credit_note.grand_total),
            "notes": credit_note.notes,
        }

    @staticmethod
    def _context_warranty_certificate(certificate, tenant):
        entity = certificate.entity
        user = certificate.created_by
        signatory_name = certificate.signatory_name or (user.full_name if user else "")
        signatory_phone = certificate.signatory_phone or (user.phone if user else "")
        signatory_email = certificate.signatory_email or (user.email if user else "")

        item_rows = []
        for item in certificate.items.all():
            item_rows.append({
                "serial_number": item.serial_number,
                "product_name": item.product_name or "—",
                "specification": item.specification or "—",
                "identifier": item.identifier or "—",
                "location": item.location or "—",
                "site_reference": item.site_reference or "—",
                "location_display": item.location_display or "—",
            })

        return {
            "filename": f"Warranty-Certificate-{certificate.reference_number}.pdf",
            "title": "Warranty Certificate",
            "entity": _entity_context(entity, tenant),
            "customer": _customer_context(certificate.customer),
            "header_meta_rows": [
                {"label": "Reference", "value": certificate.reference_number},
                {"label": "Date", "value": _format_date(certificate.certificate_date)},
                {"label": "Warranty", "value": f"{certificate.warranty_months} months"},
            ],
            "document_number": certificate.reference_number,
            "document_date": _format_date(certificate.certificate_date),
            "project_name": certificate.project_name,
            "attention_person": certificate.attention_person,
            "drn": certificate.drn,
            "finishing_date": _format_date(certificate.finishing_date),
            "warranty_end_date": _format_date(certificate.warranty_end_date),
            "customer_lpo": certificate.customer_lpo,
            "service_report_reference": certificate.service_report_reference,
            "item_rows": item_rows,
            "work_title": certificate.work_title,
            "work_description": certificate.work_description,
            "warranty_months": certificate.warranty_months,
            "warranty_statement": certificate.warranty_statement
            or certificate.build_default_warranty_statement(),
            "signatory_name": signatory_name,
            "signatory_phone": signatory_phone,
            "signatory_email": signatory_email,
            "entity_short_name": entity.name if entity else "",
            "notes": certificate.notes,
        }
