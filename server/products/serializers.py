from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Product


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        data = {key: value for key, value in validated_data.items() if key not in ("password1", "password2")}
        data["password"] = validated_data["password1"]
        return self.Meta.model.objects.create_user(**data)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "password1",
            "password2",
        )
        read_only_fields = ("id",)


class LogInSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user_data = UserSerializer(user).data
        for key, value in user_data.items():
            if key != "id":
                token[key] = value
        return token


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    price = serializers.CharField(required=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "rating",
            "average_rating",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "average_rating",
            "created_at",
            "updated_at",
        )


class ProductRatingSerializer(serializers.ModelSerializer):
    rating = serializers.CharField(required=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "rating",
            "average_rating",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "average_rating",
            "created_at",
            "updated_at",
        )

    def validate_rating(self, value):
        if float(value) < 0 or float(value) > 5:
            raise serializers.ValidationError("Rating has to be between 0 and 5.")
        return value


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()
