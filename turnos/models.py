from django.db import models
from django.core.exceptions import ValidationError

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

    def clean(self):
        """Validaciones a nivel de modelo."""
        super().clean()
        if self.hora_fin and self.hora_inicio and self.hora_fin <= self.hora_inicio:
            raise ValidationError({
                "hora_fin": "La hora de fin debe ser posterior a la hora de inicio."
            })

        # Validar solapamiento con otros turnos del mismo profesional en la misma fecha
        if self.profesional_id and self.fecha and self.hora_inicio and self.hora_fin:
            qs = Turno.objects.filter(
                profesional=self.profesional,
                fecha=self.fecha,
                estado__in=[EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO],
            ).exclude(pk=self.pk)
            for existing in qs:
                # Verificar solapamiento: nuevo.inicio < existente.fin AND nuevo.fin > existente.inicio
                if self.hora_inicio < existing.hora_fin and self.hora_fin > existing.hora_inicio:
                    raise ValidationError({
                        "hora_inicio": (
                            f"El profesional ya tiene un turno en ese horario "
                            f"({existing.hora_inicio}-{existing.hora_fin})."
                        )
                    })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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