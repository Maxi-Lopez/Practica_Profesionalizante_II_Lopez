from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ["username", "email", "rol", "area", "first_name", "last_name", "is_staff", "is_active"]
    list_filter = ["rol", "area", "is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["username"]
    autocomplete_fields = ["area"]

    fieldsets = UserAdmin.fieldsets + (
        ("Rol y Área", {"fields": ("rol", "area")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol y Área", {"fields": ("rol", "area")}),
    )