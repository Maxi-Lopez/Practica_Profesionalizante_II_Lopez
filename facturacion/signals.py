from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import FacturaVenta, DetalleVenta, Pago, EstadoFactura


def _recalcular_factura(factura):
    """Recalcula subtotal y total de una factura basándose en sus detalles."""
    subtotal = factura.detalles.aggregate(total=Sum('subtotal'))['total'] or Decimal('0')
    total = subtotal - (factura.descuento or Decimal('0'))

    FacturaVenta.objects.filter(pk=factura.pk).update(
        subtotal=subtotal,
        total=total
    )


def _recalcular_estado_factura(factura):
    """Recalcula el estado de una factura basándose en sus pagos."""
    if factura.estado == EstadoFactura.ANULADA:
        return

    total_pagado = factura.pagos.filter(anulado=False).aggregate(total=Sum('monto'))['total'] or Decimal('0')
    total_factura = factura.total or Decimal('0')

    if total_pagado >= total_factura and total_factura > 0:
        nuevo_estado = EstadoFactura.PAGADA
    elif total_pagado > 0:
        nuevo_estado = EstadoFactura.PARCIAL
    else:
        nuevo_estado = EstadoFactura.PENDIENTE

    if factura.estado != nuevo_estado:
        FacturaVenta.objects.filter(pk=factura.pk).update(estado=nuevo_estado)


@receiver(post_save, sender=DetalleVenta)
def recalcular_factura_al_guardar_detalle(sender, instance, **kwargs):
    """Al crear/actualizar un DetalleVenta, recalcula subtotal y total de la factura."""
    _recalcular_factura(instance.factura)


@receiver(post_delete, sender=DetalleVenta)
def recalcular_factura_al_borrar_detalle(sender, instance, **kwargs):
    """Al borrar un DetalleVenta, recalcula subtotal y total de la factura."""
    _recalcular_factura(instance.factura)


@receiver(post_save, sender=Pago)
def recalcular_estado_factura_al_guardar_pago(sender, instance, **kwargs):
    """Al crear/actualizar un Pago, recalcula el estado de la factura."""
    _recalcular_estado_factura(instance.factura)


@receiver(post_delete, sender=Pago)
def recalcular_estado_factura_al_borrar_pago(sender, instance, **kwargs):
    """Al borrar un Pago, recalcula el estado de la factura."""
    _recalcular_estado_factura(instance.factura)