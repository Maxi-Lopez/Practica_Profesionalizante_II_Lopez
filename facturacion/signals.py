"""Signals para facturación: recálculo automático de totales."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal

from .models import DetalleVenta, FacturaVenta


@receiver(post_save, sender=DetalleVenta)
def recalcular_total_factura_post_save(sender, instance, **kwargs):
    """Recalcula el total de la factura cuando se guarda un detalle."""
    factura = instance.factura
    if factura:
        factura.calcular_total()
        factura.save(update_fields=['subtotal', 'total'])


@receiver(post_delete, sender=DetalleVenta)
def recalcular_total_factura_post_delete(sender, instance, **kwargs):
    """Recalcula el total de la factura cuando se elimina un detalle."""
    factura = instance.factura
    if factura:
        factura.calcular_total()
        factura.save(update_fields=['subtotal', 'total'])