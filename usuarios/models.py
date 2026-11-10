from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class RolUsuario(models.TextChoices):
    ADMIN = "admin", "Administrativo"
    ORIENTADOR = "orientador", "Orientador"
    PSICOLOGO = "psicologo", "Psicólogo"
    MEDICO = "medico", "Médico"
    TRABAJADOR_SOCIAL = "trabajador_social", "Trabajador Social"
    KINESIOLOGO = "kinesiologo", "Kinesiólogo"
    PSICOMOTRICISTA = "psicomotricista", "Psicomotricista"
    NUTRICIONISTA = "nutricionista", "Nutricionista"
    PSICOPEDAGOGO = "psicopedagogo", "Psicopedagogo"
    PEDAGOGO = "pedagogo", "Pedagogo"
    ENFERMERO = "enfermero", "Enfermero"
    RECEPCIONISTA = "recepcionista", "Recepcionista"


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, rol=RolUsuario.RECEPCIONISTA, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", RolUsuario.ADMIN)
        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.RECEPCIONISTA,
    )
    area = models.ForeignKey(
        'pacientes.AreaInterdisciplinaria',
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
        help_text="Área interdisciplinaria a la que pertenece el profesional (si rol=profesional)",
    )

    objects = UsuarioManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"