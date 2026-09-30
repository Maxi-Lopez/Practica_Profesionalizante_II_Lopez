from django.db import models

from pacientes.models import Paciente
from empleados.models import Empleado
from servicios.models import Servicio


class PlanTratamiento(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="planes_tratamiento",
    )

    nombre = models.CharField(max_length=150)

    descripcion = models.TextField(blank=True)

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField(
        null=True,
        blank=True,
    )

    observaciones = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de tratamiento"
        verbose_name_plural = "Planes de tratamiento"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.paciente} - {self.nombre}"


class ObjetivoTratamiento(models.Model):
    plan_tratamiento = models.ForeignKey(
        PlanTratamiento,
        on_delete=models.PROTECT,
        related_name="objetivos",
    )

    descripcion = models.TextField()

    cumplido = models.BooleanField(default=False)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion[:80]


class ActividadPlan(models.Model):
    plan_tratamiento = models.ForeignKey(
        PlanTratamiento,
        on_delete=models.PROTECT,
        related_name="actividades",
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name="actividades_tratamiento",
        null=True,
        blank=True,
    )

    descripcion = models.TextField()

    frecuencia_semanal = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion[:80]


class HistorialMedico(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="historial_medico",
    )

    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="historiales_medicos",
    )

    fecha = models.DateTimeField()

    descripcion = models.TextField()

    observaciones = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial médico"
        verbose_name_plural = "Historiales médicos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.paciente} - {self.fecha}"


class EvolucionSemanal(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="evoluciones",
    )

    plan_tratamiento = models.ForeignKey(
        PlanTratamiento,
        on_delete=models.PROTECT,
        related_name="evoluciones",
        null=True,
        blank=True,
    )

    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="evoluciones_registradas",
    )

    fecha = models.DateField()

    descripcion = models.TextField()

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evolución semanal"
        verbose_name_plural = "Evoluciones semanales"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.paciente} - {self.fecha}"


class RegistroActividad(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="registros_actividad",
    )

    actividad = models.ForeignKey(
        ActividadPlan,
        on_delete=models.PROTECT,
        related_name="registros",
    )

    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="actividades_registradas",
    )

    fecha = models.DateTimeField()

    descripcion = models.TextField(blank=True)

    realizado = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de actividad"
        verbose_name_plural = "Registros de actividades"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.paciente} - {self.fecha}"


class NotaImportante(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="notas_importantes",
    )

    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="notas_realizadas",
    )

    titulo = models.CharField(max_length=150)

    descripcion = models.TextField()

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota importante"
        verbose_name_plural = "Notas importantes"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.paciente} - {self.titulo}"