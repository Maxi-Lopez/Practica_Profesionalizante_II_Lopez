from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Turno, AsistenciaPaciente, EstadoTurno


@receiver(post_save, sender=Turno)
def crear_asistencia_al_confirmar_turno(sender, instance, created, **kwargs):
    """
    Al confirmar o realizar un turno (estado CONFIRMADO o REALIZADO),
    crea automáticamente la AsistenciaPaciente si no existe.
    Si el turno se cancela, no crea asistencia (o elimina si existe).
    """
    if instance.estado in [EstadoTurno.CONFIRMADO, EstadoTurno.REALIZADO]:
        AsistenciaPaciente.objects.get_or_create(
            turno=instance,
            defaults={'presente': False}
        )
    elif instance.estado == EstadoTurno.CANCELADO:
        # Si el turno se cancela, eliminar la asistencia si existe
        AsistenciaPaciente.objects.filter(turno=instance).delete()