PLACEHOLDER_DESCRIPTIONS = frozenset({
    "Imported invoice balance",
    "Imported invoice balance.",
})


def build_import_invoice_description(record: dict) -> str:
    """Build a multi-line invoice line description from payment import metadata."""
    explicit = str(record.get("description") or "").strip()
    if explicit:
        return explicit

    lines: list[str] = []
    customer = str(record.get("customer_name") or "").strip()
    invoice_number = record.get("invoice_number")
    lpo = str(record.get("customer_lpo") or "").strip()
    drn = str(record.get("drn") or "").strip()
    invoice_date = record.get("invoice_date")
    remarks = str(record.get("remarks") or "").strip()
    status = str(record.get("status") or "").strip()

    if customer:
        lines.append(f"Electromechanical / maintenance works for {customer}")
    else:
        lines.append(f"Tax invoice services - Invoice #{invoice_number}")

    if lpo:
        lines.append(f"Customer LPO: {lpo}")
    if drn:
        lines.append(f"DRN: {drn}")
    if invoice_number:
        date_suffix = f" - {invoice_date}" if invoice_date else ""
        lines.append(f"Invoice #{invoice_number}{date_suffix}")

    terms = record.get("payment_terms_days")
    if terms:
        lines.append(f"Payment terms: {terms} days")

    if status:
        lines.append(f"Payment status: {status}")
    if remarks:
        lines.append(f"Remarks: {remarks}")

    return "\n".join(lines)


def should_refresh_imported_description(current_description: str, record: dict) -> bool:
    if str(record.get("description") or "").strip():
        return True
    return current_description.strip() in PLACEHOLDER_DESCRIPTIONS
