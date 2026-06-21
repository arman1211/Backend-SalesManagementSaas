from django.db import transaction


@transaction.atomic
def get_next_sequence(entity, field_name: str) -> int:
    """Atomically increment and return the next document sequence number."""
    from apps.tenants.models import CompanyEntity

    locked = CompanyEntity.objects.select_for_update().get(pk=entity.pk)
    current = getattr(locked, field_name)
    next_value = current + 1
    setattr(locked, field_name, next_value)
    locked.save(update_fields=[field_name, "updated_at"])
    return next_value
