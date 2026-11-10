from django.contrib import admin
from .models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


def anular_compras(modeladmin, request, queryset):
    queryset.update(anulada=True)
anular_compras.short_description = "Anular compras seleccionadas"


def anular_gastos(modeladmin, request, queryset):
    queryset.update(anulado=True)
anular_gastos.short_description = "Anular gastos seleccionados"


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'cuit', 'telefono', 'email', 'activo']
    list_filter = ['activo']
    search_fields = ['razon_social', 'cuit', 'email', 'direccion']
    ordering = ['razon_social']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    fieldsets = (
        ('Datos del Proveedor', {
            'fields': ('razon_social', 'cuit', 'telefono', 'email', 'direccion')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'fecha', 'numero_comprobante', 'total', 'anulada']
    list_filter = ['anulada', 'fecha', 'proveedor']
    search_fields = ['numero_comprobante', 'proveedor__razon_social', 'observaciones']
    ordering = ['-fecha']
    readonly_fields = ['fecha', 'fecha_actualizacion', 'total', 'anulada']
    inlines = [DetalleCompraInline]
    fieldsets = (
        ('Datos de la Compra', {
            'fields': ('proveedor', 'fecha', 'numero_comprobante')
        }),
        ('Montos', {
            'fields': ('total',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Estado', {
            'fields': ('anulada', 'fecha_actualizacion')
        }),
    )
    actions = [anular_compras]


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ['compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['producto__categoria', 'compra__proveedor']
    search_fields = ['compra__numero_comprobante', 'producto__nombre']
    ordering = ['compra', 'id']
    readonly_fields = ['subtotal']


@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['concepto', 'tipo_gasto', 'proveedor', 'fecha', 'monto', 'anulado']
    list_filter = ['anulado', 'fecha', 'tipo_gasto', 'proveedor']
    search_fields = ['concepto', 'numero_comprobante', 'proveedor__razon_social', 'tipo_gasto__nombre']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion', 'anulado']
    fieldsets = (
        ('Datos del Gasto', {
            'fields': ('tipo_gasto', 'proveedor', 'fecha', 'concepto', 'monto', 'numero_comprobante')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Estado', {
            'fields': ('anulado', 'fecha_creacion')
        }),
    )
    actions = [anular_gastos]