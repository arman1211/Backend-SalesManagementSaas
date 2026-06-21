from rest_framework.permissions import BasePermission


class IsTenantMember(BasePermission):
    """User must belong to an active tenant."""

    message = "You must belong to an active tenant to perform this action."

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.tenant_id is not None
            and user.is_active
        )


class IsTenantAdmin(BasePermission):
    """User must be tenant admin or platform superuser."""

    message = "Tenant admin access required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role == user.Role.TENANT_ADMIN
