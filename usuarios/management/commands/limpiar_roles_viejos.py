from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Actualiza usuarios con roles obsoletos (profesional, paciente)'

    def handle(self, *args, **kwargs):
        roles_viejos = ['profesional', 'paciente']
        usuarios = Usuario.objects.filter(rol__in=roles_viejos)

        count = 0
        for user in usuarios:
            if user.rol == 'profesional':
                user.rol = 'recepcionista'
            elif user.rol == 'paciente':
                user.rol = 'recepcionista'
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Actualizado: {user.username} -> {user.rol}'))
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Total actualizados: {count}'))