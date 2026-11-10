from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class RolUsuario(models.TextChoices):
    ADMIN = "admin", "Administrador"
    ORIENTADOR = "orientador", "Orientador de Sala"
    PROFESIONAL = "profesional", "Profesional"
    RECEPCIONISTA = "recepcionista", "Recepcionista"
    PACIENTE = "paciente", "Paciente"


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, rol=RolUsuario.PACIENTE, **extra_fields):
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
        default=RolUsuario.PACIENTE,
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