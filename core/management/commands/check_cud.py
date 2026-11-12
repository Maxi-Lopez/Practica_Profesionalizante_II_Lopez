from django.core.management.base import BaseCommand
from django.utils import timezone
from pacientes.models import Paciente


class Command(BaseCommand):
    help = 'Verifica vencimientos de CUD (Certificado Único de Discapacidad) de los pacientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Días de anticipación para alertar (default: 30)'
        )
        parser.add_argument(
            '--solo-vencidos',
            action='store_true',
            help='Solo mostrar CUDs ya vencidos'
        )
        parser.add_argument(
            '--solo-por-vencer',
            action='store_true',
            help='Solo mostrar CUDs por vencer'
        )

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        dias = options['dias']
        solo_vencidos = options['solo_vencidos']
        solo_por_vencer = options['solo_por_vencer']

        self.stdout.write(self.style.NOTICE(f'\n{"="*70}'))
        self.stdout.write(self.style.NOTICE(f'  REPORTE DE VENCIMIENTOS DE CUD - {hoy.strftime("%d/%m/%Y")}'))
        self.stdout.write(self.style.NOTICE(f'{"="*70}\n'))

        # Pacientes con CUD vencido
        if not solo_por_vencer:
            cud_vencidos = Paciente.objects.filter(
                activo=True,
                fecha_vencimiento_cud__lt=hoy
            ).select_related('persona', 'obra_social').order_by('fecha_vencimiento_cud')

            if cud_vencidos.exists():
                self.stdout.write(self.style.ERROR(f'❌ CUD VENCIDOS ({cud_vencidos.count()})'))
                self.stdout.write(self.style.ERROR('-' * 70))
                for p in cud_vencidos:
                    dias_vencido = (hoy - p.fecha_vencimiento_cud).days
                    self.stdout.write(
                        self.style.ERROR(
                            f'  {p.persona.apellido}, {p.persona.nombre} '
                            f'(DNI: {p.persona.dni}) | '
                            f'Venció: {p.fecha_vencimiento_cud.strftime("%d/%m/%Y")} '
                            f'({dias_vencido} días)'
                        )
                    )
                self.stdout.write('')
            else:
                self.stdout.write(self.style.SUCCESS('✅ No hay CUDs vencidos.\n'))

        # Pacientes con CUD por vencer
        if not solo_vencidos:
            cud_por_vencer = Paciente.objects.filter(
                activo=True,
                fecha_vencimiento_cud__gte=timezone.now().date(),
                fecha_vencimiento_cud__lte=timezone.now().date() + timezone.timedelta(days=dias)
            ).select_related('persona', 'obra_social').order_by('fecha_vencimiento_cud')

            if cud_por_vencer.exists():
                self.stdout.write(self.style.WARNING(f'⚠️  CUD POR VENCER EN {dias} DÍAS ({cud_por_vencer.count()})'))
                self.stdout.write(self.style.WARNING('-' * 70))
                for p in cud_por_vencer:
                    dias_restantes = (p.fecha_vencimiento_cud - hoy).days
                    self.stdout.write(
                        self.style.WARNING(
                            f'  {p.persona.apellido}, {p.persona.nombre} '
                            f'(DNI: {p.persona.dni}) | '
                            f'Vence: {p.fecha_vencimiento_cud.strftime("%d/%m/%Y")} '
                            f'({dias_restantes} días)'
                        )
                    )
                self.stdout.write('')
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ No hay CUDs por vencer en los próximos {dias} días.\n'))

        # Resumen
        total_vencidos = Paciente.objects.filter(activo=True, fecha_vencimiento_cud__lt=hoy).count()
        total_por_vencer = Paciente.objects.filter(
            activo=True,
            fecha_vencimiento_cud__gte=hoy,
            fecha_vencimiento_cud__lte=hoy + timezone.timedelta(days=dias)
        ).count()

        self.stdout.write(self.style.NOTICE(f'{"="*70}'))
        self.stdout.write(self.style.NOTICE(f'  RESUMEN:'))
        self.stdout.write(self.style.NOTICE(f'    - Vencidos: {total_vencidos}'))
        self.stdout.write(self.style.NOTICE(f'    - Por vencer ({dias} días): {total_por_vencer}'))
        self.stdout.write(self.style.NOTICE(f'{"="*70}\n'))