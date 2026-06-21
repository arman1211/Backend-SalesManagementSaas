from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANT = Decimal("0.01")


def quantize_money(value) -> Decimal:
    return Decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def calculate_document_totals(
    line_totals,
    discount_amount=Decimal("0.00"),
    discount_percent=None,
    vat_rate=Decimal("0.05"),
):
    """Return subtotal, discount, net_total, vat_amount, grand_total."""
    subtotal = sum(line_totals, Decimal("0.00"))
    subtotal = quantize_money(subtotal)

    discount = Decimal("0.00")
    if discount_percent is not None and discount_percent > 0:
        discount = quantize_money(subtotal * (Decimal(discount_percent) / Decimal("100")))
    elif discount_amount:
        discount = quantize_money(discount_amount)

    net_total = quantize_money(max(subtotal - discount, Decimal("0.00")))
    vat_amount = quantize_money(net_total * Decimal(vat_rate))
    grand_total = quantize_money(net_total + vat_amount)

    return {
        "subtotal": subtotal,
        "discount_amount": discount,
        "net_total": net_total,
        "vat_amount": vat_amount,
        "grand_total": grand_total,
    }
