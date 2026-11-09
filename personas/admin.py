from django.contrib import admin
from .models import Pais, Provincia, Localidad, Persona, Telefono, Email


class TelefonoInline(admin.TabularInline):
    model = Telefono
    extra = 1
    fields = ['numero', 'tipo', 'es_principal', 'activo']
    readonly_fields = ['fecha_creacion']


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1
    fields = ['direccion_email', 'tipo', 'es_principal', 'activo']
    readonly_fields = ['fecha_creacion']


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'pais', 'activo']
    list_filter = ['activo', 'pais']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_postal', 'provincia', 'activo']
    list_filter = ['activo', 'provincia__pais', 'provincia']
    search_fields = ['nombre', 'codigo_postal']
    ordering = ['nombre']


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'dni', 'localidad', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'localidad__provincia__pais', 'localidad__provincia', 'localidad']
    search_fields = ['nombre', 'apellido', 'dni']
    ordering = ['-fecha_creacion']
    inlines = [TelefonoInline, EmailInline]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Datos Personales', {
            'fields': ('nombre', 'apellido', 'dni', 'fecha_nacimiento')
        }),
        ('Dirección', {
            'fields': ('direccion', 'localidad')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(Telefono)
class TelefonoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'persona', 'tipo', 'es_principal', 'activo']
    list_filter = ['activo', 'tipo', 'es_principal']
    search_fields = ['numero', 'persona__nombre', 'persona__apellido']
    ordering = ['-fecha_creacion']


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['direccion_email', 'persona', 'tipo', 'es_principal', 'activo']
    list_filter = ['activo', 'tipo', 'es_principal']
    search_fields = ['direccion_email', 'persona__nombre', 'persona__apellido']
    ordering = ['-fecha_creacion']