from django.contrib import admin
from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'persona', 'tipo', 'nombre', 'fecha_documento', 'fecha_vencimiento', 'activo', 'fecha_creacion']
    list_filter = ['tipo', 'activo', 'fecha_creacion', 'persona__localidad__provincia']
    search_fields = ['nombre', 'descripcion', 'persona__nombre', 'persona__apellido', 'persona__dni']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    raw_id_fields = ['persona']