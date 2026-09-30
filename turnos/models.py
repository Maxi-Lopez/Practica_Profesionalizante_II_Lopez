from django.db import models

from pacientes.models import Paciente
from empleados.models import Empleado
from servicios.models import Servicio
from tratamientos.models import PlanTratamiento


class EstadoTurno(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    CONFIRMADO = "CONFIRMADO", "Confirmado"
    REALIZADO = "REALIZADO", "Realizado"
    CANCELADO = "CANCELADO", "Cancelado"
    AUSENTE = "AUSENTE", "Ausente"


class Turno(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="turnos",
    )

    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="turnos",
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="turnos",
    )

    plan_tratamiento = models.ForeignKey(
        PlanTratamiento,
        on_delete=models.PROTECT,
        related_name="turnos",
        null=True,
        blank=True,
    )

    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    estado = models.CharField(
        max_length=20,
        choices=EstadoTurno.choices,
        default=EstadoTurno.PENDIENTE,
    )

    observaciones = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ["-fecha", "-hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["profesional", "fecha", "hora_inicio"],
                name="unique_turno_profesional_fecha_hora",
            )
        ]

    def __str__(self):
        return (
            f"{self.paciente} - "
            f"{self.fecha} {self.hora_inicio} - "
            f"{self.servicio}"
        )


class AsistenciaPaciente(models.Model):
    turno = models.OneToOneField(
        Turno,
        on_delete=models.PROTECT,
        related_name="asistencia",
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    presente = models.BooleanField(default=True)

    hora_llegada = models.TimeField(
        null=True,
        blank=True,
    )

    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Asistencia del paciente"
        verbose_name_plural = "Asistencias de pacientes"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.turno.paciente} - {self.turno.fecha}"