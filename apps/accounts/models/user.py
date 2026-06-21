from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.accounts.managers.user import UserManager
from apps.core.models.base import TimeStampedModel, UUIDModel


class User(UUIDModel, TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    """Custom user model with email login and tenant association."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        TENANT_ADMIN = "tenant_admin", "Tenant Admin"
        ACCOUNTANT = "accountant", "Accountant"
        ACCOUNT_MANAGER = "account_manager", "Account Manager"
        TECHNICIAN = "technician", "Technician"
        VIEWER = "viewer", "Viewer"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.VIEWER,
    )
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["email"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
