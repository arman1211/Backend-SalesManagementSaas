from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers.user import UserSerializer
from apps.tenants.models import Tenant


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is deactivated.")

        refresh = RefreshToken.for_user(user)
        attrs["user"] = user
        attrs["tokens"] = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return attrs

    def to_representation(self, instance):
        return {
            "user": UserSerializer(instance["user"]).data,
            "tokens": instance["tokens"],
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        self.token = value
        return value

    def save(self, **kwargs):
        from rest_framework_simplejwt.tokens import RefreshToken

        try:
            RefreshToken(self.token).blacklist()
        except Exception as exc:
            raise serializers.ValidationError("Invalid or expired refresh token.") from exc


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    tenant_name = serializers.CharField(write_only=True, max_length=255)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "tenant_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        from django.utils.text import slugify

        tenant_name = validated_data.pop("tenant_name")
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        base_slug = slugify(tenant_name)[:90] or "tenant"
        slug = base_slug
        counter = 1
        while Tenant.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        tenant = Tenant.objects.create(name=tenant_name, slug=slug)

        from apps.tenants.models import CompanyEntity

        CompanyEntity.objects.create(
            tenant=tenant,
            name=tenant_name,
            legal_name=tenant_name,
            is_default=True,
            next_invoice_number=2009,
        )

        user = User.objects.create_user(
            password=password,
            tenant=tenant,
            role=User.Role.TENANT_ADMIN,
            **validated_data,
        )
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            "user": UserSerializer(instance).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }
