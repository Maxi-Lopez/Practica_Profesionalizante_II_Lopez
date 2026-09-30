from django.db import models

from personas.models import Persona


class Documento(models.Model):
    class TipoDocumento(models.TextChoices):
        DNI = "DNI", "DNI"
        CUD = "CUD", "Certificado Único de Discapacidad"
        ORDEN_MEDICA = "ORDEN_MEDICA", "Orden médica"
        ESTUDIO = "ESTUDIO", "Estudio"
        CERTIFICADO = "CERTIFICADO", "Certificado"
        CONSENTIMIENTO = "CONSENTIMIENTO", "Consentimiento"
        OTRO = "OTRO", "Otro"

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="documentos",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoDocumento.choices,
        default=TipoDocumento.OTRO,
    )

    nombre = models.CharField(max_length=200)

    archivo = models.FileField(
        upload_to="documentos/%Y/%m/",
    )

    descripcion = models.TextField(blank=True)

    fecha_documento = models.DateField(
        null=True,
        blank=True,
    )

    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.persona} - {self.nombre}"