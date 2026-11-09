from django.contrib import admin
from .models import CategoriaProducto, Producto, MovimientoStock


class MovimientoStockInline(admin.TabularInline):
    model = MovimientoStock
    extra = 0
    fields = ['tipo', 'cantidad', 'stock_anterior', 'stock_resultante', 'motivo', 'fecha']
    readonly_fields = ['fecha', 'stock_resultante']
    ordering = ['-fecha']


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'codigo', 'stock_actual', 'stock_minimo', 'precio_compra', 'precio_venta', 'activo']
    list_filter = ['activo', 'categoria']
    search_fields = ['nombre', 'descripcion', 'codigo']
    ordering = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'stock_actual']
    inlines = [MovimientoStockInline]
    fieldsets = (
        ('Datos del Producto', {
            'fields': ('categoria', 'nombre', 'descripcion', 'codigo')
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo')
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_resultante', 'fecha']
    list_filter = ['tipo', 'fecha', 'producto__categoria']
    search_fields = ['producto__nombre', 'motivo']
    ordering = ['-fecha']
    readonly_fields = ['fecha']