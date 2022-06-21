from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import Product, User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "name",
        "price",
        "rating",
        "updated_at",
    )
    list_display = (
        "id",
        "name",
        "price",
        "rating",
        "updated_at",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
