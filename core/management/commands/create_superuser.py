import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Crear o actualizar superusuario automáticamente desde variables de entorno"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Variables DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD requeridas. Saltando creación."
                )
            )
            return

        user, created = User.objects.get_or_create(username=username, defaults={"email": email or ""})

        user.email = email or ""
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superusuario '{username}' actualizado (contraseña reseteada).")
            )