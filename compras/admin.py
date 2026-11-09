from django.contrib import admin
from .models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    readonly_fields = ['subtotal']
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']


class GastoInline(admin.TabularInline):
    model = Gasto
    extra = 1
    fields = ['tipo_gasto', 'proveedor', 'fecha', 'concepto', 'monto', 'numero_comprobante', 'anulado']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'cuit', 'telefono', 'email', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['razon_social', 'cuit', 'email', 'direccion']
    ordering = ['razon_social']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(TipoGasto)
class TipoGastoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'fecha', 'numero_comprobante', 'total', 'anulada']
    list_filter = ['anulada', 'proveedor', 'fecha']
    search_fields = ['numero_comprobante', 'proveedor__razon_social', 'observaciones']
    ordering = ['-fecha']
    readonly_fields = ['fecha', 'fecha_actualizacion']
    inlines = [DetalleCompraInline]


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['compra__proveedor', 'producto__categoria']
    search_fields = ['compra__numero_comprobante', 'producto__nombre', 'producto__codigo']
    readonly_fields = ['subtotal']
    ordering = ['-compra__fecha']


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_gasto', 'proveedor', 'fecha', 'concepto', 'monto', 'anulado']
    list_filter = ['tipo_gasto', 'proveedor', 'anulado', 'fecha']
    search_fields = ['concepto', 'numero_comprobante', 'tipo_gasto__nombre', 'proveedor__razon_social']
    ordering = ['-fecha']
    readonly_fields = ['fecha_creacion']