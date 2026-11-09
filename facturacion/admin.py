from django.contrib import admin
from .models import FacturaVenta, DetalleVenta, Pago, EstadoFactura


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ['servicio', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1
    fields = ['fecha', 'monto', 'medio_pago', 'referencia', 'anulado']
    readonly_fields = ['fecha']


@admin.register(FacturaVenta)
class FacturaVentaAdmin(admin.ModelAdmin):
    list_display = ['numero_factura', 'paciente', 'obra_social', 'fecha', 'estado', 'subtotal', 'descuento', 'total']
    list_filter = ['estado', 'fecha', 'obra_social', 'paciente__persona__localidad__provincia']
    search_fields = ['numero_factura', 'paciente__persona__nombre', 'paciente__persona__apellido', 'paciente__persona__dni']
    ordering = ['-fecha']
    readonly_fields = ['fecha', 'fecha_actualizacion', 'total']
    inlines = [DetalleVentaInline, PagoInline]
    fieldsets = (
        ('Datos de la Factura', {
            'fields': ('paciente', 'obra_social', 'numero_factura', 'fecha')
        }),
        ('Montos', {
            'fields': ('subtotal', 'descuento', 'total')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('fecha_actualizacion',)
        }),
    )


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['factura', 'servicio', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['servicio__tipo_servicio', 'factura__estado']
    search_fields = ['factura__numero_factura', 'descripcion', 'servicio__nombre']
    ordering = ['factura', 'id']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['factura', 'fecha', 'monto', 'medio_pago', 'anulado']
    list_filter = ['medio_pago', 'anulado', 'fecha', 'factura__estado']
    search_fields = ['factura__numero_factura', 'referencia']
    ordering = ['-fecha']
    readonly_fields = ['fecha']