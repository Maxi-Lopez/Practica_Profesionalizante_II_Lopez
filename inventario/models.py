from django.db import models


class CategoriaProducto(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
    )

    descripcion = models.CharField(
        max_length=255,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
    )

    nombre = models.CharField(max_length=150)

    descripcion = models.TextField(blank=True)

    codigo = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )

    stock_actual = models.PositiveIntegerField(default=0)

    stock_minimo = models.PositiveIntegerField(default=0)

    precio_compra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    precio_venta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class MovimientoStock(models.Model):
    class TipoMovimiento(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        AJUSTE = "AJUSTE", "Ajuste"

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )

    tipo = models.CharField(
        max_length=10,
        choices=TipoMovimiento.choices,
    )

    cantidad = models.PositiveIntegerField()

    stock_anterior = models.PositiveIntegerField()

    stock_resultante = models.PositiveIntegerField()

    motivo = models.CharField(
        max_length=255,
        blank=True,
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        ordering = ["-fecha"]

    def __str__(self):
        return (
            f"{self.producto} - "
            f"{self.get_tipo_display()} - "
            f"{self.cantidad}"
        )