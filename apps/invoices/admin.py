from django.contrib import admin

from apps.invoices.models import Invoice, InvoiceLineItem


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number", "customer", "invoice_date", "grand_total",
        "payment_status", "balance_amount", "status",
    )
    list_filter = ("payment_status", "status", "tenant")
    inlines = [InvoiceLineItemInline]
