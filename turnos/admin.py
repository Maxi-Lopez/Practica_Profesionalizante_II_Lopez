from django.contrib import admin
from .models import Turno, AsistenciaPaciente, EstadoTurno


class AsistenciaPacienteInline(admin.TabularInline):
    model = AsistenciaPaciente
    extra = 0
    fields = ['presente', 'hora_llegada', 'observaciones']
    readonly_fields = ['fecha_registro']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'servicio', 'fecha', 'hora_inicio', 'hora_fin', 'estado']
    list_filter = ['estado', 'fecha', 'profesional', 'servicio__tipo_servicio']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'profesional__persona__nombre', 'profesional__persona__apellido', 'servicio__nombre']
    ordering = ['-fecha', '-hora_inicio']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [AsistenciaPacienteInline]
    fieldsets = (
        ('Datos del Turno', {
            'fields': ('paciente', 'profesional', 'servicio', 'plan_tratamiento')
        }),
        ('Fecha y Hora', {
            'fields': ('fecha', 'hora_inicio', 'hora_fin')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(AsistenciaPaciente)
class AsistenciaPacienteAdmin(admin.ModelAdmin):
    list_display = ['turno', 'presente', 'hora_llegada', 'fecha_registro']
    list_filter = ['presente', 'turno__fecha']
    search_fields = ['turno__paciente__persona__nombre', 'turno__paciente__persona__apellido']
    ordering = ['-fecha_registro']
    readonly_fields = ['fecha_registro']