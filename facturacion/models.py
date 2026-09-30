from django.db import models

from pacientes.models import Paciente, ObraSocial
from servicios.models import Servicio


class EstadoFactura(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    PAGADA = "PAGADA", "Pagada"
    PARCIAL = "PARCIAL", "Pago parcial"
    ANULADA = "ANULADA", "Anulada"


class FacturaVenta(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="facturas",
    )

    obra_social = models.ForeignKey(
        ObraSocial,
        on_delete=models.PROTECT,
        related_name="facturas",
        null=True,
        blank=True,
    )

    numero_factura = models.CharField(
        max_length=50,
        unique=True,
    )

    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=EstadoFactura.choices,
        default=EstadoFactura.PENDIENTE,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    observaciones = models.TextField(blank=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Factura de venta"
        verbose_name_plural = "Facturas de venta"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.numero_factura} - {self.paciente}"


class DetalleVenta(models.Model):
    factura = models.ForeignKey(
        FacturaVenta,
        on_delete=models.PROTECT,
        related_name="detalles",
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="detalles_facturacion",
        null=True,
        blank=True,
    )

    descripcion = models.CharField(max_length=255)

    cantidad = models.PositiveIntegerField(default=1)

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.factura.numero_factura} - {self.descripcion}"


class Pago(models.Model):
    class MedioPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        DEBITO = "DEBITO", "Tarjeta de débito"
        CREDITO = "CREDITO", "Tarjeta de crédito"
        OTRO = "OTRO", "Otro"

    factura = models.ForeignKey(
        FacturaVenta,
        on_delete=models.PROTECT,
        related_name="pagos",
    )

    fecha = models.DateTimeField(auto_now_add=True)

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    medio_pago = models.CharField(
        max_length=20,
        choices=MedioPago.choices,
    )

    referencia = models.CharField(
        max_length=100,
        blank=True,
    )

    observaciones = models.TextField(blank=True)

    anulado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.factura.numero_factura} - ${self.monto}"