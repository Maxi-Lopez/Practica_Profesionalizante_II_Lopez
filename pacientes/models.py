from django.db import models

from personas.models import Persona


class ObraSocial(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(max_length=80, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=150, blank=True)
    cuit = models.CharField(max_length=20, blank=True, unique=True)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Obra social"
        verbose_name_plural = "Obras sociales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    persona = models.OneToOneField(
        Persona,
        on_delete=models.PROTECT,
        related_name="paciente",
    )

    historia_clinica = models.CharField(
        max_length=80,
        blank=True,
        unique=True,
    )

    numero_cud = models.CharField(
        max_length=100,
        blank=True,
    )

    fecha_vencimiento_cud = models.DateField(
        null=True,
        blank=True,
    )

    obra_social = models.ForeignKey(
        ObraSocial,
        on_delete=models.PROTECT,
        related_name="pacientes",
        null=True,
        blank=True,
    )

    nro_afiliado = models.CharField(
        max_length=100,
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

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["persona__apellido", "persona__nombre"]

    def __str__(self):
        return str(self.persona)


class ResponsablePaciente(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="responsables",
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="pacientes_a_cargo",
    )

    parentesco = models.CharField(
        max_length=80,
        blank=True,
    )

    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Responsable del paciente"
        verbose_name_plural = "Responsables de pacientes"
        constraints = [
            models.UniqueConstraint(
                fields=["paciente", "persona"],
                name="unique_responsable_paciente",
            )
        ]

    def __str__(self):
        return f"{self.persona} - Responsable de {self.paciente}"


class TipoDiagnostico(models.Model):
    nombre = models.CharField(
        max_length=80,
        unique=True,
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de diagnóstico"
        verbose_name_plural = "Tipos de diagnóstico"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Diagnostico(models.Model):
    tipo = models.ForeignKey(
        TipoDiagnostico,
        on_delete=models.PROTECT,
        related_name="diagnosticos",
    )

    nombre = models.CharField(max_length=200)

    descripcion = models.TextField(blank=True)

    codigo_cie10 = models.CharField(
        max_length=20,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo", "nombre"],
                name="unique_diagnostico_tipo",
            )
        ]

    def __str__(self):
        return self.nombre


class PacienteDiagnostico(models.Model):
    class TipoRegistro(models.TextChoices):
        REAL = "REAL", "Real"
        CUD = "CUD", "CUD"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="diagnosticos",
    )

    diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.PROTECT,
        related_name="pacientes",
    )

    tipo = models.CharField(
        max_length=10,
        choices=TipoRegistro.choices,
        default=TipoRegistro.REAL,
    )

    fecha_registro = models.DateField(auto_now_add=True)

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Diagnóstico del paciente"
        verbose_name_plural = "Diagnósticos de pacientes"
        constraints = [
            models.UniqueConstraint(
                fields=["paciente", "diagnostico", "tipo"],
                name="unique_paciente_diagnostico_tipo",
            )
        ]

    def __str__(self):
        return f"{self.paciente} - {self.diagnostico}"