from django.db import models

from empleados.models import Empleado
from pacientes.models import ObraSocial


class TipoServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de servicio"
        verbose_name_plural = "Tipos de servicio"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    tipo_servicio = models.ForeignKey(
        TipoServicio,
        on_delete=models.PROTECT,
        related_name="servicios",
    )

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    precio_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    duracion_minutos = models.PositiveIntegerField(default=60)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_servicio", "nombre"],
                name="unique_servicio_tipo",
            )
        ]

    def __str__(self):
        return self.nombre


class ProfesionalServicio(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="servicios_profesionales",
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="profesionales",
    )

    activo = models.BooleanField(default=True)

    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Servicio del profesional"
        verbose_name_plural = "Servicios de profesionales"
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "servicio"],
                name="unique_profesional_servicio",
            )
        ]

    def __str__(self):
        return f"{self.empleado} - {self.servicio}"


class ServicioObraSocial(models.Model):
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="obras_sociales",
    )

    obra_social = models.ForeignKey(
        ObraSocial,
        on_delete=models.PROTECT,
        related_name="servicios",
    )

    precio_autorizado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    codigo_obra_social = models.CharField(
        max_length=50,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Servicio por obra social"
        verbose_name_plural = "Servicios por obras sociales"
        constraints = [
            models.UniqueConstraint(
                fields=["servicio", "obra_social"],
                name="unique_servicio_obra_social",
            )
        ]

    def __str__(self):
        return f"{self.servicio} - {self.obra_social}"