from decimal import Decimal

from apps.core.services.calculations import calculate_document_totals


def apply_totals_to_document(document, line_items, vat_rate=None):
    discount_amount = getattr(document, "discount_amount", Decimal("0.00"))
    discount_percent = getattr(document, "discount_percent", None)
    totals = calculate_document_totals(
        line_totals=[item.line_total for item in line_items],
        discount_amount=discount_amount,
        discount_percent=discount_percent,
        vat_rate=vat_rate or document.vat_rate,
    )
    document.subtotal = totals["subtotal"]
    if hasattr(document, "discount_amount"):
        document.discount_amount = totals["discount_amount"]
    if hasattr(document, "net_total"):
        document.net_total = totals["net_total"]
    document.vat_amount = totals["vat_amount"]
    document.grand_total = totals["grand_total"]
    return document


def sync_line_items(parent, items_data, model_class, fk_name, existing_qs=None):
    """Replace line items on a document."""
    if existing_qs is None:
        existing_qs = getattr(parent, "line_items").all()

    existing_qs.delete()
    created = []
    for index, item_data in enumerate(items_data, start=1):
        item_data = dict(item_data)
        item_data.pop("id", None)
        item_data["serial_number"] = item_data.get("serial_number", index)
        created.append(model_class.objects.create(**{fk_name: parent}, **item_data))
    return created
