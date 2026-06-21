from django.contrib import admin

from apps.quotations.models import Quotation, QuotationLineItem


class QuotationLineItemInline(admin.TabularInline):
    model = QuotationLineItem
    extra = 0


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("reference_number", "customer", "quotation_date", "grand_total", "status")
    inlines = [QuotationLineItemInline]
