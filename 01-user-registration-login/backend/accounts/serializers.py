from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "phone", "language", "date_joined", "is_staff"]
        read_only_fields = ["id", "email", "date_joined", "is_staff"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["email", "full_name", "phone", "language", "password"]

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        # Run Django's password rules (length, common, numeric-only, too similar to the email).
        candidate = User(email=attrs.get("email"), full_name=attrs.get("full_name", ""))
        password_validation.validate_password(attrs["password"], candidate)
        return attrs

    def create(self, validated):
        # create_user hashes the password; it is never stored in plain text.
        return User.objects.create_user(**validated)


class EmailTokenSerializer(TokenObtainPairSerializer):
    """Login with email + password; response also carries the user profile."""

    def validate(self, attrs):
        attrs[self.username_field] = attrs.get(self.username_field, "").lower().strip()
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data