from django.contrib import admin
from .models import TipoServicio, Servicio, ProfesionalServicio, ServicioObraSocial


class ProfesionalServicioInline(admin.TabularInline):
    model = ProfesionalServicio
    extra = 1
    fields = ['empleado', 'activo']
    readonly_fields = ['fecha_asignacion']


class ServicioObraSocialInline(admin.TabularInline):
    model = ServicioObraSocial
    extra = 1
    fields = ['obra_social', 'precio_autorizado', 'codigo_obra_social', 'activo']


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_servicio', 'precio_base', 'duracion_minutos', 'activo']
    list_filter = ['activo', 'tipo_servicio']
    search_fields = ['nombre', 'descripcion', 'tipo_servicio__nombre']
    ordering = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [ProfesionalServicioInline, ServicioObraSocialInline]
    fieldsets = (
        ('Datos del Servicio', {
            'fields': ('tipo_servicio', 'nombre', 'descripcion')
        }),
        ('Precio y Duración', {
            'fields': ('precio_base', 'duracion_minutos')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(ProfesionalServicio)
class ProfesionalServicioAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'servicio', 'activo', 'fecha_asignacion']
    list_filter = ['activo', 'servicio__tipo_servicio', 'empleado']
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido', 'servicio__nombre']
    ordering = ['-fecha_asignacion']
    readonly_fields = ['fecha_asignacion']


@admin.register(ServicioObraSocial)
class ServicioObraSocialAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'obra_social', 'precio_autorizado', 'codigo_obra_social', 'activo']
    list_filter = ['activo', 'obra_social', 'servicio__tipo_servicio']
    search_fields = ['servicio__nombre', 'obra_social__nombre', 'codigo_obra_social']
    ordering = ['servicio', 'obra_social']