from django.contrib import admin

from apps.credit_notes.models import CreditNote, CreditNoteLineItem


class CreditNoteLineItemInline(admin.TabularInline):
    model = CreditNoteLineItem
    extra = 0


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ("credit_note_number", "customer", "original_invoice", "grand_total", "status")
    inlines = [CreditNoteLineItemInline]
