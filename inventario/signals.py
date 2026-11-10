from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MovimientoStock, Producto


@receiver(post_save, sender=MovimientoStock)
def actualizar_stock_producto(sender, instance, created, **kwargs):
    """
    Al crear un MovimientoStock, actualiza automáticamente el stock_actual del Producto.
    También actualiza stock_anterior y stock_resultante del movimiento si no fueron seteados.
    """
    if not created:
        return

    producto = instance.producto

    with transaction.atomic():
        # Bloquear el producto para evitar race conditions
        producto = Producto.objects.select_for_update().get(pk=producto.pk)

        stock_anterior = producto.stock_actual

        if instance.tipo == MovimientoStock.TipoMovimiento.ENTRADA:
            stock_resultante = stock_anterior + instance.cantidad
        elif instance.tipo == MovimientoStock.TipoMovimiento.SALIDA:
            stock_resultante = stock_anterior - instance.cantidad
            if stock_resultante < 0:
                raise ValueError(
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Stock actual: {stock_anterior}, solicitado: {instance.cantidad}"
                )
        elif instance.tipo == MovimientoStock.TipoMovimiento.AJUSTE:
            stock_resultante = instance.cantidad
        else:
            raise ValueError(f"Tipo de movimiento inválido: {instance.tipo}")

        # Actualizar stock del producto
        producto.stock_actual = stock_resultante
        producto.save(update_fields=['stock_actual', 'fecha_actualizacion'])

        # Actualizar el movimiento con stock_anterior y stock_resultante calculados
        # Usar update() para evitar recursión del signal
        MovimientoStock.objects.filter(pk=instance.pk).update(
            stock_anterior=stock_anterior,
            stock_resultante=stock_resultante
        )