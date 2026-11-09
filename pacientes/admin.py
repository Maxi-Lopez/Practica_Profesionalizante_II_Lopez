from django.contrib import admin
from .models import ObraSocial, Paciente, ResponsablePaciente, TipoDiagnostico, Diagnostico, PacienteDiagnostico


class ResponsablePacienteInline(admin.TabularInline):
    model = ResponsablePaciente
    extra = 1
    fields = ['persona', 'parentesco', 'es_principal', 'activo']
    readonly_fields = ['fecha_creacion']


class PacienteDiagnosticoInline(admin.TabularInline):
    model = PacienteDiagnostico
    extra = 1
    fields = ['diagnostico', 'tipo', 'activo']
    readonly_fields = ['fecha_registro']


@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'cuit', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'codigo', 'cuit', 'email']
    ordering = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(TipoDiagnostico)
class TipoDiagnosticoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'codigo_cie10', 'activo']
    list_filter = ['activo', 'tipo']
    search_fields = ['nombre', 'descripcion', 'codigo_cie10']
    ordering = ['nombre']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['persona', 'historia_clinica', 'obra_social', 'nro_afiliado', 'activo', 'fecha_ingreso']
    list_filter = ['activo', 'obra_social', 'persona__localidad__provincia']
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'historia_clinica', 'nro_afiliado']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [ResponsablePacienteInline, PacienteDiagnosticoInline]
    fieldsets = (
        ('Datos del Paciente', {
            'fields': ('persona', 'historia_clinica', 'numero_cud', 'fecha_vencimiento_cud')
        }),
        ('Obra Social', {
            'fields': ('obra_social', 'nro_afiliado')
        }),
        ('Fechas', {
            'fields': ('fecha_ingreso', 'fecha_baja')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(ResponsablePaciente)
class ResponsablePacienteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'persona', 'parentesco', 'es_principal', 'activo']
    list_filter = ['activo', 'es_principal']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'persona__nombre', 'persona__apellido', 'parentesco']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion']


@admin.register(PacienteDiagnostico)
class PacienteDiagnosticoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'diagnostico', 'tipo', 'activo', 'fecha_registro']
    list_filter = ['activo', 'tipo', 'diagnostico__tipo']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'diagnostico__nombre']
    ordering = ['-fecha_registro']
    readonly_fields = ['fecha_registro']