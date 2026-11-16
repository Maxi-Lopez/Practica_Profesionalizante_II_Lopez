import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Crear superusuario automáticamente desde variables de entorno"

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

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Superusuario '{username}' ya existe. Saltando creación.")
            )
            return

        User.objects.create_superuser(username=username, email=email or "", password=password)
        self.stdout.write(
            self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente.")
        )