from django.contrib import admin

from apps.warranty_certificates.models import WarrantyCertificate, WarrantyCertificateItem


class WarrantyCertificateItemInline(admin.TabularInline):
    model = WarrantyCertificateItem
    extra = 0


@admin.register(WarrantyCertificate)
class WarrantyCertificateAdmin(admin.ModelAdmin):
    list_display = ("reference_number", "customer", "certificate_date", "status")
    list_filter = ("status",)
    search_fields = ("reference_number", "customer__name", "project_name")
    inlines = [WarrantyCertificateItemInline]
