from django.contrib import admin
from .models import (
    PlanTratamiento, ObjetivoTratamiento, ActividadPlan,
    HistorialMedico, EvolucionSemanal, RegistroActividad, NotaImportante
)


class ObjetivoTratamientoInline(admin.TabularInline):
    model = ObjetivoTratamiento
    extra = 1
    fields = ['descripcion', 'cumplido', 'activo']
    readonly_fields = ['fecha_creacion']


class ActividadPlanInline(admin.TabularInline):
    model = ActividadPlan
    extra = 1
    fields = ['servicio', 'descripcion', 'frecuencia_semanal', 'activo']
    readonly_fields = ['fecha_creacion']


class RegistroActividadInline(admin.TabularInline):
    model = RegistroActividad
    extra = 1
    fields = ['actividad', 'profesional', 'fecha', 'realizado']
    readonly_fields = ['fecha_creacion']


@admin.register(PlanTratamiento)
class PlanTratamientoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre', 'fecha_inicio', 'fecha_fin', 'activo']
    list_filter = ['activo', 'fecha_inicio', 'paciente__persona__localidad__provincia']
    search_fields = ['nombre', 'descripcion', 'paciente__persona__nombre', 'paciente__persona__apellido']
    ordering = ['-fecha_inicio']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [ObjetivoTratamientoInline, ActividadPlanInline]
    fieldsets = (
        ('Datos del Plan', {
            'fields': ('paciente', 'nombre', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(ObjetivoTratamiento)
class ObjetivoTratamientoAdmin(admin.ModelAdmin):
    list_display = ['plan_tratamiento', 'descripcion', 'cumplido', 'activo']
    list_filter = ['cumplido', 'activo', 'plan_tratamiento']
    search_fields = ['descripcion', 'plan_tratamiento__nombre']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion']


@admin.register(ActividadPlan)
class ActividadPlanAdmin(admin.ModelAdmin):
    list_display = ['plan_tratamiento', 'servicio', 'descripcion', 'frecuencia_semanal', 'activo']
    list_filter = ['activo', 'plan_tratamiento', 'servicio__tipo_servicio']
    search_fields = ['descripcion', 'plan_tratamiento__nombre', 'servicio__nombre']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion']
    inlines = [RegistroActividadInline]


@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'fecha']
    list_filter = ['fecha', 'profesional', 'paciente__persona__localidad__provincia']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'profesional__persona__nombre', 'descripcion']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']


@admin.register(EvolucionSemanal)
class EvolucionSemanalAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'plan_tratamiento', 'profesional', 'fecha']
    list_filter = ['fecha', 'profesional', 'plan_tratamiento', 'paciente__persona__localidad__provincia']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'plan_tratamiento__nombre', 'descripcion']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']


@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'actividad', 'profesional', 'fecha', 'realizado']
    list_filter = ['realizado', 'fecha', 'profesional', 'actividad__plan_tratamiento']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'actividad__descripcion']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']


@admin.register(NotaImportante)
class NotaImportanteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'titulo', 'fecha']
    list_filter = ['fecha', 'profesional', 'paciente__persona__localidad__provincia']
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'titulo', 'descripcion']
    ordering = ['-fecha']
    readonly_fields = ['fecha']