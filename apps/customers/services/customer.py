from apps.customers.models import Customer, CustomerContact


class CustomerService:
    @staticmethod
    def create_customer(tenant, **validated_data):
        contacts_data = validated_data.pop("contacts", [])
        customer = Customer.objects.create(tenant=tenant, **validated_data)

        for contact_data in contacts_data:
            CustomerContact.objects.create(customer=customer, **contact_data)

        return customer

    @staticmethod
    def get_tenant_customers(tenant):
        return Customer.objects.filter(tenant=tenant).prefetch_related("contacts")
