from django.db import models


class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(
        Pais,
        on_delete=models.PROTECT,
        related_name="provincias",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "pais"],
                name="unique_provincia_pais",
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.pais.nombre}"


class Localidad(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_postal = models.CharField(
        max_length=20,
        blank=True,
    )
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        related_name="localidades",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "provincia"],
                name="unique_localidad_provincia",
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.provincia.nombre}"


class Persona(models.Model):
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)

    dni = models.CharField(
        max_length=30,
        unique=True,
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
    )

    localidad = models.ForeignKey(
        Localidad,
        on_delete=models.PROTECT,
        related_name="personas",
        null=True,
        blank=True,
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} - DNI {self.dni}"


class Telefono(models.Model):
    class TipoTelefono(models.TextChoices):
        CELULAR = "CELULAR", "Celular"
        FIJO = "FIJO", "Fijo"
        LABORAL = "LABORAL", "Laboral"
        OTRO = "OTRO", "Otro"

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="telefonos",
    )

    numero = models.CharField(max_length=50)

    tipo = models.CharField(
        max_length=10,
        choices=TipoTelefono.choices,
        default=TipoTelefono.CELULAR,
    )

    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Teléfono"
        verbose_name_plural = "Teléfonos"

    def __str__(self):
        return f"{self.numero} - {self.persona}"


class Email(models.Model):
    class TipoEmail(models.TextChoices):
        PERSONAL = "PERSONAL", "Personal"
        LABORAL = "LABORAL", "Laboral"
        OTRO = "OTRO", "Otro"

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="emails",
    )

    direccion_email = models.EmailField(max_length=200)

    tipo = models.CharField(
        max_length=10,
        choices=TipoEmail.choices,
        default=TipoEmail.PERSONAL,
    )

    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    def __str__(self):
        return f"{self.direccion_email} - {self.persona}"