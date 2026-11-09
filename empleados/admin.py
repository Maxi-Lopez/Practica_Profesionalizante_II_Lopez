from django.contrib import admin
from .models import Rol, Empleado, EmpleadoRol, HorarioEmpleado, AsistenciaEmpleado


class EmpleadoRolInline(admin.TabularInline):
    model = EmpleadoRol
    extra = 1
    fields = ['rol', 'activo']
    readonly_fields = ['fecha_asignacion']


class HorarioEmpleadoInline(admin.TabularInline):
    model = HorarioEmpleado
    extra = 1
    fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['persona', 'matricula', 'fecha_ingreso', 'horas_semanales', 'activo']
    list_filter = ['activo', 'persona__localidad__provincia']
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'matricula']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [EmpleadoRolInline, HorarioEmpleadoInline]
    fieldsets = (
        ('Datos del Empleado', {
            'fields': ('persona', 'matricula')
        }),
        ('Fechas', {
            'fields': ('fecha_ingreso', 'fecha_baja', 'horas_semanales')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(EmpleadoRol)
class EmpleadoRolAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'rol', 'activo', 'fecha_asignacion']
    list_filter = ['activo', 'rol']
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido', 'rol__nombre']
    ordering = ['-fecha_asignacion']
    readonly_fields = ['fecha_asignacion']


@admin.register(HorarioEmpleado)
class HorarioEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['activo', 'dia_semana', 'empleado']
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido']
    ordering = ['empleado', 'dia_semana', 'hora_inicio']


@admin.register(AsistenciaEmpleado)
class AsistenciaEmpleadoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'fecha', 'hora_entrada', 'hora_salida']
    list_filter = ['fecha', 'empleado']
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']