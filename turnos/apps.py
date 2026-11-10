from django.apps import AppConfig


class TurnosConfig(AppConfig):
    name = 'turnos'

    def ready(self):
        import turnos.signals  # noqa: F401
