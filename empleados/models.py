from django.db import models

from personas.models import Persona


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    persona = models.OneToOneField(
        Persona,
        on_delete=models.PROTECT,
        related_name="empleado",
    )

    matricula = models.CharField(
        max_length=50,
        blank=True,
    )

    fecha_ingreso = models.DateField(
        null=True,
        blank=True,
    )

    fecha_baja = models.DateField(
        null=True,
        blank=True,
    )

    horas_semanales = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["persona__apellido", "persona__nombre"]

    def __str__(self):
        return str(self.persona)


class EmpleadoRol(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="roles",
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name="empleados",
    )

    activo = models.BooleanField(default=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol del empleado"
        verbose_name_plural = "Roles de empleados"
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "rol"],
                name="unique_empleado_rol",
            )
        ]

    def __str__(self):
        return f"{self.empleado} - {self.rol}"


class HorarioEmpleado(models.Model):
    class DiaSemana(models.TextChoices):
        LUNES = "LUNES", "Lunes"
        MARTES = "MARTES", "Martes"
        MIERCOLES = "MIERCOLES", "Miércoles"
        JUEVES = "JUEVES", "Jueves"
        VIERNES = "VIERNES", "Viernes"
        SABADO = "SABADO", "Sábado"

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="horarios",
    )

    dia_semana = models.CharField(
        max_length=10,
        choices=DiaSemana.choices,
    )

    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Horario del empleado"
        verbose_name_plural = "Horarios de empleados"
        ordering = ["empleado", "dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "empleado",
                    "dia_semana",
                    "hora_inicio",
                    "hora_fin",
                ],
                name="unique_horario_empleado",
            )
        ]

    def __str__(self):
        return (
            f"{self.empleado} - "
            f"{self.get_dia_semana_display()} "
            f"{self.hora_inicio} a {self.hora_fin}"
        )


class AsistenciaEmpleado(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="asistencias",
    )

    fecha = models.DateField()
    hora_entrada = models.TimeField(
        null=True,
        blank=True,
    )
    hora_salida = models.TimeField(
        null=True,
        blank=True,
    )
    observaciones = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asistencia del empleado"
        verbose_name_plural = "Asistencias de empleados"
        ordering = ["-fecha"]
        constraints = [
            models.UniqueConstraint(
                fields=["empleado", "fecha"],
                name="unique_asistencia_empleado_fecha",
            )
        ]

    def __str__(self):
        return f"{self.empleado} - {self.fecha}"