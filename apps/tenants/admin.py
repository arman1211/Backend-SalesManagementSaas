from django.contrib import admin

from apps.tenants.models import CompanyEntity, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "trn", "email", "created_at")
    list_filter = ("status", "country")
    search_fields = ("name", "slug", "trn", "email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(CompanyEntity)
class CompanyEntityAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "trn", "is_default", "next_invoice_number")
    list_filter = ("tenant", "is_default")
    search_fields = ("name", "trn")
