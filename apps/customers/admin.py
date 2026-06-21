from django.contrib import admin

from apps.customers.models import Customer, CustomerContact


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "customer_code", "tenant", "trn", "status", "city")
    list_filter = ("status", "tenant", "city")
    search_fields = ("name", "customer_code", "trn", "email")
    inlines = [CustomerContactInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "designation", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("name", "customer__name")
