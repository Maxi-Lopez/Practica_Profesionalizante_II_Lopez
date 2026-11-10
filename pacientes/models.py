from django.db import models

from personas.models import Persona
from empleados.models import Empleado


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


class Sala(models.Model):
    """Salas del centro de día. Cada sala tiene un orientador a cargo y planificación de actividades."""
    nombre = models.CharField(max_length=100, unique=True)
    orientador = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="salas_orientadas",
        null=True,
        blank=True,
    )
    planificacion_actividades = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class AreaInterdisciplinaria(models.Model):
    """Áreas interdisciplinarias que atienden a los concurrentes."""
    class NombreArea(models.TextChoices):
        PSICOLOGIA = "psicologia", "Psicología"
        MEDICA = "medica", "Médica"
        TRABAJO_SOCIAL = "trabajo_social", "Trabajo Social"
        KINESIOLOGIA = "kinesiologia", "Kinesiología"
        PSICOMOTRICIDAD = "psicomotricidad", "Psicomotricidad"
        NUTRICION = "nutricion", "Nutrición"
        PSICOPEDAGOGIA = "psicopedagogia", "Psicopedagogía"
        PEDAGOGIA_ESPECIAL = "pedagogia_especial", "Pedagogía Especial"

    nombre = models.CharField(
        max_length=30,
        choices=NombreArea.choices,
        unique=True,
    )
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Área Interdisciplinaria"
        verbose_name_plural = "Áreas Interdisciplinarias"
        ordering = ["nombre"]

    def __str__(self):
        return self.get_nombre_display()


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
        help_text="Número de legajo del concurrente",
    )

    # Datos del legajo / concurrente
    numero_cud = models.CharField(
        max_length=100,
        blank=True,
    )

    fecha_vencimiento_cud = models.DateField(
        null=True,
        blank=True,
    )

    # Aviso 1 mes antes del vencimiento del CUD
    aviso_vencimiento_cud = models.BooleanField(
        default=False,
        help_text="Indica si ya se notificó el vencimiento próximo del CUD (1 mes antes)",
    )

    # Figura de apoyo (curador, tutor, etc.)
    figura_apoyo_nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre de la figura de apoyo (curador, tutor, representante legal)",
    )
    figura_apoyo_telefono = models.CharField(
        max_length=50,
        blank=True,
        help_text="Teléfono de contacto de la figura de apoyo",
    )

    # Pases de transporte con vencimiento
    pases_transporte_vencimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de vencimiento de los pases de transporte",
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

    # Sala asignada
    sala = models.ForeignKey(
        Sala,
        on_delete=models.PROTECT,
        related_name="pacientes",
        null=True,
        blank=True,
    )

    # Estado de admisión
    class EstadoAdmision(models.TextChoices):
        EN_LISTA_ESPERA = "en_lista_espera", "En lista de espera"
        FICHA_ADMISION = "ficha_admision", "Ficha de admisión cargada"
        APTO_INGRESO = "apto_ingreso", "Apto para ingreso"
        ACTIVO = "activo", "Activo"
        BAJA = "baja", "Baja"

    estado_admision = models.CharField(
        max_length=20,
        choices=EstadoAdmision.choices,
        default=EstadoAdmision.FICHA_ADMISION,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paciente (Concurrente)"
        verbose_name_plural = "Pacientes (Concurrentes)"
        ordering = ["persona__apellido", "persona__nombre"]

    def __str__(self):
        return str(self.persona)


class DiagnosticoArea(models.Model):
    """Diagnóstico inicial por área interdisciplinaria."""
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="diagnosticos_area",
    )
    area = models.ForeignKey(
        AreaInterdisciplinaria,
        on_delete=models.PROTECT,
        related_name="diagnosticos",
    )
    fecha = models.DateField()
    diagnostico = models.TextField()
    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="diagnosticos_realizados",
        null=True,
        blank=True,
    )
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Diagnóstico por Área"
        verbose_name_plural = "Diagnósticos por Área"
        ordering = ["-fecha"]
        constraints = [
            models.UniqueConstraint(
                fields=["paciente", "area", "fecha"],
                name="unique_diagnostico_paciente_area_fecha",
            )
        ]

    def __str__(self):
        return f"{self.paciente} - {self.area} ({self.fecha})"


class SeguimientoTrimestral(models.Model):
    """Seguimiento trimestral por área interdisciplinaria. Algunas áreas también tienen intervenciones mensuales."""
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="seguimientos_trimestrales",
    )
    area = models.ForeignKey(
        AreaInterdisciplinaria,
        on_delete=models.PROTECT,
        related_name="seguimientos",
    )
    fecha = models.DateField()
    observaciones = models.TextField()
    profesional = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="seguimientos_realizados",
        null=True,
        blank=True,
    )
    # Para distinguir seguimientos trimestrales de intervenciones mensuales
    es_intervencion_mensual = models.BooleanField(
        default=False,
        help_text="Marcar si es una intervención mensual (algunas áreas lo requieren)",
    )
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Seguimiento Trimestral"
        verbose_name_plural = "Seguimientos Trimestrales"
        ordering = ["-fecha"]

    def __str__(self):
        tipo = "Intervención mensual" if self.es_intervencion_mensual else "Seguimiento trimestral"
        return f"{self.paciente} - {self.area} - {tipo} ({self.fecha})"


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