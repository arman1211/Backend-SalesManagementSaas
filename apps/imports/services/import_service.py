from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.customers.models import Customer
from apps.imports.services.descriptions import (
    build_import_invoice_description,
    should_refresh_imported_description,
)
from apps.imports.services.excel_parser import (
    list_workbook_sheets,
    parse_customer_rows,
    parse_payment_rows,
)
from apps.invoices.models import Invoice
from apps.invoices.services.invoice import InvoiceService
from apps.invoices.services.receivable import refresh_invoice_receivable
from apps.payments.models import Payment
from apps.payments.services.payment import PaymentService
from apps.tenants.models import CompanyEntity


class ImportService:
    @staticmethod
    def _to_date(value):
        if not value:
            return timezone.localdate()
        if hasattr(value, "year"):
            return value
        return datetime.fromisoformat(str(value)).date()

    @staticmethod
    def _parse(uploaded_file, import_type, sheet_name=None):
        if import_type == "customers":
            return parse_customer_rows(uploaded_file, sheet_name)
        if import_type == "payments":
            return parse_payment_rows(uploaded_file, sheet_name)
        raise ValueError("Unsupported import type.")

    @staticmethod
    def preview(uploaded_file, import_type, sheet_name=None):
        rows, errors, meta = ImportService._parse(uploaded_file, import_type, sheet_name)
        return {
            "import_type": import_type,
            "sheet": meta["sheet"],
            "header_row": meta["header_row"],
            "headers_found": meta["headers_found"],
            "available_sheets": meta["available_sheets"],
            "total_rows": len(rows) + len(errors),
            "valid_rows": len(rows),
            "error_count": len(errors),
            "errors": errors[:50],
            "preview": rows[:50],
        }

    @staticmethod
    @transaction.atomic
    def execute(tenant, user, uploaded_file, import_type, sheet_name=None):
        if import_type == "customers":
            return ImportService._import_customers(tenant, uploaded_file, sheet_name)
        if import_type == "payments":
            return ImportService._import_payments(tenant, user, uploaded_file, sheet_name)
        raise ValueError("Unsupported import type.")

    @staticmethod
    def list_sheets(uploaded_file):
        return list_workbook_sheets(uploaded_file)

    @staticmethod
    def _import_customers(tenant, uploaded_file, sheet_name=None):
        rows, errors, meta = parse_customer_rows(uploaded_file, sheet_name)
        created = 0
        updated = 0
        for row in rows:
            record = row["record"]
            code = record.get("customer_code")
            customer = None
            if code:
                customer = Customer.objects.filter(
                    tenant=tenant, customer_code=code
                ).first()
            if not customer:
                customer = Customer.objects.filter(
                    tenant=tenant, name__iexact=record["name"]
                ).first()
            payload = {
                "name": record["name"],
                "trn": record.get("trn", ""),
                "email": record.get("email", ""),
                "phone": record.get("phone", ""),
                "address_line_1": record.get("address_line_1", ""),
                "address_line_2": record.get("address_line_2", ""),
                "city": record.get("city", "Abu Dhabi"),
                "country": record.get("country", "UAE"),
                "notes": record.get("notes", ""),
            }
            if code:
                payload["customer_code"] = code
            if record.get("default_payment_terms_days"):
                payload["default_payment_terms_days"] = record["default_payment_terms_days"]
            if customer:
                for field, value in payload.items():
                    setattr(customer, field, value)
                customer.save()
                updated += 1
            else:
                Customer.objects.create(tenant=tenant, **payload)
                created += 1
        return {
            "import_type": "customers",
            "sheet": meta["sheet"],
            "created": created,
            "updated": updated,
            "skipped": len(errors),
            "errors": errors[:50],
        }

    @staticmethod
    def _import_payments(tenant, user, uploaded_file, sheet_name=None):
        rows, errors, meta = parse_payment_rows(uploaded_file, sheet_name)
        entity = CompanyEntity.objects.filter(tenant=tenant, is_default=True).first()
        if not entity:
            entity = CompanyEntity.objects.filter(tenant=tenant).first()
        if not entity:
            raise ValueError("No company entity found. Complete company setup first.")

        invoices_created = 0
        payments_created = 0
        customers_created = 0
        descriptions_updated = 0

        for row in rows:
            record = row["record"]
            customer = ImportService._resolve_customer(tenant, record)
            if not customer:
                customer = Customer.objects.create(
                    tenant=tenant,
                    customer_code=record.get("customer_code"),
                    name=record.get("customer_name") or f"Customer {record['invoice_number']}",
                )
                customers_created += 1

            invoice = Invoice.objects.filter(
                tenant=tenant,
                entity=entity,
                invoice_number=record["invoice_number"],
            ).first()

            grand_total = Decimal(record["grand_total"])
            amount_received = Decimal(record["amount_received"])
            description = build_import_invoice_description(record)

            if not invoice:
                net_total = (grand_total / (Decimal("1") + tenant.default_vat_rate)).quantize(
                    Decimal("0.01")
                )
                invoice = InvoiceService.create(
                    tenant=tenant,
                    user=user,
                    entity=entity,
                    customer=customer,
                    invoice_number=record["invoice_number"],
                    invoice_date=ImportService._to_date(record.get("invoice_date")),
                    customer_lpo=record.get("customer_lpo", ""),
                    drn=record.get("drn", ""),
                    payment_terms_days=record.get("payment_terms_days", tenant.default_payment_terms_days),
                    remarks=record.get("remarks", ""),
                    retention_rate=tenant.default_retention_rate,
                    late_fee_rate=tenant.default_late_fee_rate,
                    line_items=[{
                        "serial_number": 1,
                        "description": description,
                        "unit_price": net_total,
                        "quantity": 1,
                    }],
                )
                invoice.status = Invoice.Status.ISSUED
                invoice.save(update_fields=["status", "updated_at"])
                invoices_created += 1
            else:
                invoice.customer = customer
                invoice.customer_lpo = record.get("customer_lpo", invoice.customer_lpo)
                invoice.drn = record.get("drn", invoice.drn)
                invoice.remarks = record.get("remarks", invoice.remarks)
                invoice.save()
                if ImportService._sync_imported_line_description(invoice, record):
                    descriptions_updated += 1

            if amount_received > 0:
                existing = invoice.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")
                delta = amount_received - existing
                if delta > 0:
                    PaymentService.record_payment(
                        tenant=tenant,
                        user=user,
                        invoice=invoice,
                        amount=delta,
                        payment_date=ImportService._to_date(record.get("payment_date")),
                        payment_method=Payment.PaymentMethod.BANK_TRANSFER,
                        notes="Imported from Excel",
                    )
                    payments_created += 1

            refresh_invoice_receivable(invoice)

        return {
            "import_type": "payments",
            "sheet": meta["sheet"],
            "customers_created": customers_created,
            "invoices_created": invoices_created,
            "payments_created": payments_created,
            "descriptions_updated": descriptions_updated,
            "skipped": len(errors),
            "errors": errors[:50],
        }

    @staticmethod
    def _resolve_customer(tenant, record):
        if record.get("customer_code"):
            customer = Customer.objects.filter(
                tenant=tenant, customer_code=record["customer_code"]
            ).first()
            if customer:
                return customer
        if record.get("customer_name"):
            return Customer.objects.filter(
                tenant=tenant, name__iexact=record["customer_name"]
            ).first()
        return None

    @staticmethod
    def _sync_imported_line_description(invoice, record) -> bool:
        items = list(invoice.line_items.all())
        if len(items) != 1:
            return False
        item = items[0]
        if not should_refresh_imported_description(item.description, record):
            return False
        description = build_import_invoice_description(record)
        if item.description.strip() == description.strip():
            return False
        item.description = description
        item.save(update_fields=["description", "updated_at"])
        return True
