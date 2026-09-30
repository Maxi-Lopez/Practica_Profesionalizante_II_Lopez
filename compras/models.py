from django.db import models

from inventario.models import Producto


class Proveedor(models.Model):
    razon_social = models.CharField(max_length=150)

    cuit = models.CharField(
        max_length=20,
        unique=True,
    )

    telefono = models.CharField(
        max_length=50,
        blank=True,
    )

    email = models.EmailField(
        max_length=150,
        blank=True,
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


class Compra(models.Model):
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="compras",
    )

    fecha = models.DateTimeField(auto_now_add=True)

    numero_comprobante = models.CharField(
        max_length=100,
        blank=True,
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    observaciones = models.TextField(blank=True)

    anulada = models.BooleanField(default=False)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Compra {self.id} - {self.proveedor}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.PROTECT,
        related_name="detalles",
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_compra",
    )

    cantidad = models.PositiveIntegerField()

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"

    def __str__(self):
        return f"{self.compra} - {self.producto}"


class TipoGasto(models.Model):
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
        verbose_name = "Tipo de gasto"
        verbose_name_plural = "Tipos de gastos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Gasto(models.Model):
    tipo_gasto = models.ForeignKey(
        TipoGasto,
        on_delete=models.PROTECT,
        related_name="gastos",
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="gastos",
        null=True,
        blank=True,
    )

    fecha = models.DateField()

    concepto = models.CharField(max_length=255)

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    numero_comprobante = models.CharField(
        max_length=100,
        blank=True,
    )

    observaciones = models.TextField(blank=True)

    anulado = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.concepto} - ${self.monto}"