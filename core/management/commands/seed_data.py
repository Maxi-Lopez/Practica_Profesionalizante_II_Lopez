import random
from datetime import date, time, timedelta, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker

from personas.models import Pais, Provincia, Localidad, Persona, Telefono, Email
from pacientes.models import ObraSocial, Paciente, Sala, AreaInterdisciplinaria, DiagnosticoArea, SeguimientoTrimestral
from empleados.models import Rol, Empleado, EmpleadoRol, HorarioEmpleado
from servicios.models import TipoServicio, Servicio
from turnos.models import Turno, AsistenciaPaciente, EstadoTurno
from tratamientos.models import (
    PlanTratamiento, ObjetivoTratamiento, ActividadPlan,
    HistorialMedico, EvolucionSemanal, RegistroActividad, NotaImportante
)
from facturacion.models import FacturaVenta, DetalleVenta, Pago, EstadoFactura
from inventario.models import CategoriaProducto, Producto, MovimientoStock
from compras.models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto
from documentos.models import Documento

Usuario = get_user_model()
fake = Faker('es_AR')
Faker.seed(42)
random.seed(42)


class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba para testing visual'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Limpiar datos existentes antes de poblar')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpiando datos existentes...')
            self.clear_data()

        self.stdout.write('Iniciando seed de datos...')

        # 1. Usuarios base
        usuarios = self.seed_usuarios()
        self.stdout.write(f'Usuarios: {len(usuarios)}')

        # 2. Geografía
        pais, provincias, localidades = self.seed_geografia()
        self.stdout.write(f'Pais: 1, Provincias: {len(provincias)}, Localidades: {len(localidades)}')

        # 3. Personas y contactos
        personas, telefonos, emails = self.seed_personas(localidades)
        self.stdout.write(f'Personas: {len(personas)}, Telefonos: {len(telefonos)}, Emails: {len(emails)}')

        # 4. Obras sociales
        obras_sociales = self.seed_obras_sociales()
        self.stdout.write(f'Obras sociales: {len(obras_sociales)}')

        # 5. Áreas
        areas = self.seed_areas()
        self.stdout.write(f'Areas: {len(areas)}')

        # 8. Empleados (needed before salas)
        roles_emp = self.seed_roles_empleado()
        empleados = self.seed_empleados(personas, roles_emp, usuarios)
        empleado_roles = self.seed_empleado_roles(empleados, roles_emp)
        horarios = self.seed_horarios(empleados)
        self.stdout.write(f'Empleados: {len(empleados)}, Roles: {len(empleado_roles)}, Horarios: {len(horarios)}')

        # 5b. Salas (after empleados)
        salas = self.seed_salas(areas, empleados)
        self.stdout.write(f'Salas: {len(salas)}')

        # 6. Pacientes
        pacientes = self.seed_pacientes(personas, obras_sociales, salas, usuarios)
        self.stdout.write(f'Pacientes: {len(pacientes)}')

        # 7. Diagnósticos y Seguimientos
        diagnosticos = self.seed_diagnosticos(pacientes, areas, empleados)
        seguimientos = self.seed_seguimientos(pacientes, areas, empleados)
        self.stdout.write(f'Diagnosticos: {len(diagnosticos)}, Seguimientos: {len(seguimientos)}')

        # 8. Empleados
        roles_emp = self.seed_roles_empleado()
        empleados = self.seed_empleados(personas, roles_emp, usuarios)
        empleado_roles = self.seed_empleado_roles(empleados, roles_emp)
        horarios = self.seed_horarios(empleados)
        self.stdout.write(f'Empleados: {len(empleados)}, Roles: {len(empleado_roles)}, Horarios: {len(horarios)}')

        # 9. Servicios
        tipos_servicio = self.seed_tipos_servicio()
        servicios = self.seed_servicios(tipos_servicio)
        self.stdout.write(f'Tipos servicio: {len(tipos_servicio)}, Servicios: {len(servicios)}')

        # 10. Turnos y Asistencias
        turnos = self.seed_turnos(pacientes, empleados, servicios)
        asistencias = self.seed_asistencias(turnos)
        self.stdout.write(f'Turnos: {len(turnos)}, Asistencias: {len(asistencias)}')

        # 11. Tratamientos
        planes = self.seed_planes_tratamiento(pacientes, usuarios)
        objetivos = self.seed_objetivos(planes)
        actividades = self.seed_actividades(planes, servicios, empleados)
        historiales = self.seed_historiales(pacientes, usuarios)
        evoluciones = self.seed_evoluciones(pacientes, planes, usuarios)
        registros = self.seed_registros(actividades)
        notas = self.seed_notas(pacientes, usuarios)
        self.stdout.write(f'Planes: {len(planes)}, Objetivos: {len(objetivos)}, Actividades: {len(actividades)}')
        self.stdout.write(f'Historiales: {len(historiales)}, Evoluciones: {len(evoluciones)}, Registros: {len(registros)}, Notas: {len(notas)}')

        # 12. Facturación
        facturas = self.seed_facturas(pacientes, obras_sociales)
        detalles_fact = self.seed_detalles_factura(facturas, servicios)
        pagos = self.seed_pagos(facturas)
        self.stdout.write(f'Facturas: {len(facturas)}, Detalles: {len(detalles_fact)}, Pagos: {len(pagos)}')

        # 13. Inventario
        categorias = self.seed_categorias_producto()
        productos = self.seed_productos(categorias)
        movimientos = self.seed_movimientos_stock(productos)
        self.stdout.write(f'Categorias: {len(categorias)}, Productos: {len(productos)}, Movimientos: {len(movimientos)}')

        # 14. Compras
        proveedores = self.seed_proveedores()
        compras = self.seed_compras(proveedores, productos)
        detalles_compra = self.seed_detalles_compra(compras, productos)
        tipos_gasto = self.seed_tipos_gasto()
        gastos = self.seed_gastos(tipos_gasto, proveedores)
        self.stdout.write(f'Proveedores: {len(proveedores)}, Compras: {len(compras)}, Detalles compra: {len(detalles_compra)}')
        self.stdout.write(f'Tipos gasto: {len(tipos_gasto)}, Gastos: {len(gastos)}')

        # 15. Documentos
        documentos = self.seed_documentos(personas)
        self.stdout.write(f'Documentos: {len(documentos)}')

        self.stdout.write(self.style.SUCCESS('\n✅ Seed completado exitosamente!'))

    def clear_data(self):
        models = [
            Documento, Gasto, DetalleCompra, Compra, TipoGasto, Proveedor,
            MovimientoStock, Producto, CategoriaProducto,
            Pago, DetalleVenta, FacturaVenta,
            NotaImportante, RegistroActividad, EvolucionSemanal, HistorialMedico,
            ActividadPlan, ObjetivoTratamiento, PlanTratamiento,
            AsistenciaPaciente, Turno,
            Servicio, TipoServicio,
            HorarioEmpleado, EmpleadoRol, Empleado, Rol,
            SeguimientoTrimestral, DiagnosticoArea,
            Sala, AreaInterdisciplinaria,
            Paciente, ObraSocial,
            Telefono, Email, Persona, Localidad, Provincia, Pais,
        ]
        # Delete Usuarios first (they reference AreaInterdisciplinaria)
        Usuario.objects.filter(is_superuser=False).delete()
        for model in models:
            model.objects.all().delete()

    # ==================== SEED METHODS ====================

    def seed_usuarios(self):
        usuarios = []
        data = [
            ('admin', 'admin@centrodia.com', 'Admin', 'Sistema', 'admin'),
            ('psicologo1', 'psicologo1@centrodia.com', 'Ana', 'García', 'psicologo'),
            ('medico1', 'medico1@centrodia.com', 'Carlos', 'López', 'medico'),
            ('trabajador_social1', 'ts1@centrodia.com', 'María', 'Fernández', 'trabajador_social'),
            ('kinesiologo1', 'kine1@centrodia.com', 'Roberto', 'Martínez', 'kinesiologo'),
            ('psicomotricista1', 'psicomot1@centrodia.com', 'Laura', 'Sánchez', 'psicomotricista'),
            ('nutricionista1', 'nutri1@centrodia.com', 'Sofia', 'Romero', 'nutricionista'),
            ('psicopedagogo1', 'psicoped1@centrodia.com', 'Diego', 'Torres', 'psicopedagogo'),
            ('pedagogo1', 'pedagogo1@centrodia.com', 'Lucia', 'Vargas', 'pedagogo'),
            ('enfermero1', 'enfermero1@centrodia.com', 'Pedro', 'Castro', 'enfermero'),
            ('orientador1', 'orientador1@centrodia.com', 'Elena', 'Morales', 'orientador'),
            ('recepcionista1', 'recepcionista1@centrodia.com', 'Andrea', 'Rojas', 'recepcionista'),
            ('recepcionista2', 'recepcionista2@centrodia.com', 'Jorge', 'Herrera', 'recepcionista'),
        ]
        for username, email, first, last, rol in data:
            user, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first, 'last_name': last, 'rol': rol}
            )
            if not user.check_password('testpass123'):
                user.set_password('testpass123')
                user.save()
            usuarios.append(user)
        return usuarios

    def seed_geografia(self):
        pais, _ = Pais.objects.get_or_create(nombre='Argentina', defaults={'activo': True})
        provincias_data = ['Buenos Aires', 'Córdoba', 'Santa Fe', 'Mendoza', 'Tucumán']
        provincias = []
        for nombre in provincias_data:
            prov, _ = Provincia.objects.get_or_create(nombre=nombre, pais=pais, defaults={'activo': True})
            provincias.append(prov)
        localidades = []
        loc_data = [
            ('Córdoba Capital', 5000, provincias[1]),
            ('Villa Carlos Paz', 5152, provincias[1]),
            ('Río Cuarto', 5800, provincias[1]),
            ('Rosario', 2000, provincias[2]),
            ('Santa Fe Capital', 3000, provincias[2]),
            ('Mendoza Capital', 5500, provincias[3]),
            ('San Miguel de Tucumán', 4000, provincias[4]),
        ]
        for nombre, cp, prov in loc_data:
            loc, _ = Localidad.objects.get_or_create(nombre=nombre, provincia=prov, defaults={'codigo_postal': cp, 'activo': True})
            localidades.append(loc)
        return pais, provincias, localidades

    def seed_personas(self, localidades):
        personas = []
        telefonos = []
        emails = []
        for i in range(50):
            loc = random.choice(localidades)
            dni = f'{random.randint(20000000, 50000000):08d}'
            persona, _ = Persona.objects.get_or_create(
                dni=dni,
                defaults={
                    'nombre': fake.first_name(),
                    'apellido': fake.last_name(),
                    'fecha_nacimiento': fake.date_of_birth(minimum_age=5, maximum_age=90),
                    'direccion': fake.street_address(),
                    'localidad': loc,
                    'activo': True,
                }
            )
            personas.append(persona)
            for _ in range(random.randint(1, 2)):
                tel, _ = Telefono.objects.get_or_create(
                    persona=persona,
                    numero=fake.phone_number()[:20],
                    defaults={
                        'tipo': random.choice(['CELULAR', 'FIJO', 'LABORAL']),
                        'es_principal': _ == 0,
                        'activo': True,
                    }
                )
                telefonos.append(tel)
            email, _ = Email.objects.get_or_create(
                persona=persona,
                direccion_email=fake.unique.email(),
                defaults={
                    'tipo': random.choice(['PERSONAL', 'LABORAL']),
                    'es_principal': True,
                    'activo': True,
                }
            )
            emails.append(email)
        return personas, telefonos, emails

    def seed_obras_sociales(self):
        obras = []
        data = [
            ('OSDE', '210', '0800-222-6733', 'osde@osde.com.ar', '30-12345678-9'),
            ('Swiss Medical', '215', '0800-333-7947', 'info@swissmedical.com.ar', '30-23456789-0'),
            ('Galeno', '220', '0800-444-4253', 'contacto@galeno.com.ar', '30-34567890-1'),
            ('OSPEDYC', '225', '0800-555-7339', 'info@ospedyc.com.ar', '30-45678901-2'),
            ('IOMA', '230', '0800-666-4662', 'info@ioma.gba.gov.ar', '30-56789012-3'),
            ('PAMI', '235', '0800-777-4264', 'info@pami.org.ar', '30-67890123-4'),
            ('OSPE', '240', '0800-888-7737', 'info@ospe.com.ar', '30-78901234-5'),
            ('OSPRERA', '245', '0800-999-7773', 'info@osprera.com.ar', '30-89012345-6'),
        ]
        for nombre, codigo, tel, email, cuit in data:
            obra, _ = ObraSocial.objects.get_or_create(
                nombre=nombre,
                defaults={'codigo': codigo, 'telefono': tel, 'email': email, 'cuit': cuit, 'activo': True}
            )
            obras.append(obra)
        return obras

    def seed_areas(self):
        areas = []
        for choice in AreaInterdisciplinaria.NombreArea.choices:
            area, _ = AreaInterdisciplinaria.objects.get_or_create(
                nombre=choice[0],
                defaults={'descripcion': f'Área de {choice[1]}', 'activo': True}
            )
            areas.append(area)
        return areas

    def seed_salas(self, areas, empleados):
        orientadores = [e for e in empleados if hasattr(e, 'persona') and hasattr(e.persona, 'usuario') and e.persona.usuario.rol == 'orientador']
        # If no orientador employees, use any employee
        if not orientadores:
            orientadores = empleados
        salas = []
        for i in range(1, 9):
            sala, _ = Sala.objects.get_or_create(
                nombre=f'Sala {i}',
                defaults={
                    'orientador': random.choice(orientadores) if orientadores else None,
                    'planificacion_actividades': fake.text(max_nb_chars=200),
                    'activo': True,
                }
            )
            salas.append(sala)
        return salas

    def seed_pacientes(self, personas, obras_sociales, salas, usuarios):
        pacientes = []
        personas_sin_paciente = [p for p in personas if not hasattr(p, 'paciente')]
        for persona in personas_sin_paciente[:25]:
            obra = random.choice(obras_sociales)
            sala = random.choice(salas)
            paciente, _ = Paciente.objects.get_or_create(
                persona=persona,
                defaults={
                    'historia_clinica': f'HC-{persona.dni[-6:]}',
                    'obra_social': obra,
                    'nro_afiliado': f'{random.randint(100000, 999999)}',
                    'fecha_ingreso': fake.date_between(start_date='-3y', end_date='today'),
                    'numero_cud': f'CUD-{random.randint(1000000, 9999999)}' if random.random() > 0.3 else '',
                    'fecha_vencimiento_cud': fake.future_date(end_date='+2y') if random.random() > 0.3 else None,
                    'aviso_vencimiento_cud': random.random() > 0.5,
                    'figura_apoyo_nombre': fake.name() if random.random() > 0.4 else '',
                    'figura_apoyo_telefono': fake.phone_number()[:20] if random.random() > 0.4 else '',
                    'pases_transporte_vencimiento': fake.future_date(end_date='+1y') if random.random() > 0.5 else None,
                    'sala': sala,
                    'estado_admision': random.choice(['activo', 'activo', 'activo', 'en_lista_espera', 'apto_ingreso']),
                    'activo': True,
                }
            )
            pacientes.append(paciente)
        return pacientes

    def seed_diagnosticos(self, pacientes, areas, empleados):
        diagnosticos = []
        for paciente in random.sample(pacientes, min(len(pacientes), 20)):
            for area in random.sample(areas, random.randint(1, 3)):
                diag, _ = DiagnosticoArea.objects.get_or_create(
                    paciente=paciente,
                    area=area,
                    defaults={
                        'fecha': fake.date_between(start_date='-2y', end_date='today'),
                        'diagnostico': fake.text(max_nb_chars=300),
                        'profesional': random.choice(empleados),
                        'activo': True,
                    }
                )
                diagnosticos.append(diag)
        return diagnosticos

    def seed_seguimientos(self, pacientes, areas, empleados):
        seguimientos = []
        for paciente in random.sample(pacientes, min(len(pacientes), 15)):
            for area in random.sample(areas, random.randint(1, 2)):
                for _ in range(random.randint(1, 3)):
                    seg, _ = SeguimientoTrimestral.objects.get_or_create(
                        paciente=paciente,
                        area=area,
                        defaults={
                            'fecha': fake.date_between(start_date='-1y', end_date='today'),
                            'observaciones': fake.text(max_nb_chars=400),
                            'profesional': random.choice(empleados),
                            'es_intervencion_mensual': random.random() > 0.7,
                            'activo': True,
                        }
                    )
                    seguimientos.append(seg)
        return seguimientos

    def seed_roles_empleado(self):
        roles = []
        data = [
            ('Psicólogo', 'Profesional de psicología'),
            ('Médico', 'Médico general o especialista'),
            ('Trabajador Social', 'Profesional de trabajo social'),
            ('Kinesiólogo', 'Profesional de kinesiología'),
            ('Psicomotricista', 'Profesional de psicomotricidad'),
            ('Nutricionista', 'Profesional de nutrición'),
            ('Psicopedagogo', 'Profesional de psicopedagogía'),
            ('Pedagogo', 'Profesional de pedagogía especial'),
            ('Enfermero', 'Profesional de enfermería'),
            ('Orientador', 'Responsable de sala'),
            ('Recepcionista', 'Atención al público y administración'),
            ('Administrativo', 'Tareas administrativas'),
        ]
        for nombre, desc in data:
            rol, _ = Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc, 'activo': True})
            roles.append(rol)
        return roles

    def seed_empleados(self, personas, roles, usuarios):
        empleados = []
        personas_libres = [p for p in personas if not hasattr(p, 'paciente') and not hasattr(p, 'empleado')]
        matriculas_usadas = set()
        for i, persona in enumerate(personas_libres[:15]):
            matricula = f'MAT-{persona.dni}-{i+1:03d}'
            emp = Empleado.objects.filter(persona=persona).first()
            if not emp:
                emp = Empleado.objects.create(
                    persona=persona,
                    fecha_ingreso=fake.date_between(start_date='-5y', end_date='today'),
                    matricula=matricula,
                    activo=True,
                )
            empleados.append(emp)
        return empleados

    def seed_empleado_roles(self, empleados, roles):
        emp_roles = []
        for emp in empleados:
            rol = random.choice(roles)
            er, _ = EmpleadoRol.objects.get_or_create(
                empleado=emp,
                rol=rol,
                defaults={
                    'fecha_asignacion': fake.date_between(start_date='-2y', end_date='today'),
                    'activo': True,
                }
            )
            emp_roles.append(er)
        return emp_roles

    def seed_horarios(self, empleados):
        horarios = []
        dias = list(range(1, 6))
        for emp in empleados:
            for dia in random.sample(dias, random.randint(3, 5)):
                hora_inicio = time(random.randint(8, 10), 0)
                hora_fin = time(hora_inicio.hour + random.randint(4, 8), 0)
                hor_obj, _ = HorarioEmpleado.objects.get_or_create(
                    empleado=emp,
                    dia_semana=dia,
                    defaults={
                        'hora_inicio': hora_inicio,
                        'hora_fin': hora_fin,
                        'activo': True,
                    }
                )
                horarios.append(hor_obj)
        return horarios

    def seed_tipos_servicio(self):
        tipos = []
        data = [
            ('Consulta Médica', 'Consultas médicas generales y especializadas'),
            ('Terapia Psicológica', 'Sesiones de psicoterapia individual o grupal'),
            ('Kinesiterapia', 'Tratamientos de kinesiología y rehabilitación'),
            ('Psicomotricidad', 'Sesiones de psicomotricidad'),
            ('Trabajo Social', 'Intervención en trabajo social'),
            ('Nutrición', 'Consultas nutricionales'),
            ('Psicopedagogía', 'Evaluación y tratamiento psicopedagógico'),
            ('Pedagogía Especial', 'Intervención pedagógica especializada'),
            ('Enfermería', 'Controles de enfermería'),
        ]
        for nombre, desc in data:
            tipo, _ = TipoServicio.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc, 'activo': True})
            tipos.append(tipo)
        return tipos

    def seed_servicios(self, tipos_servicio):
        servicios = []
        for tipo in tipos_servicio:
            for i in range(random.randint(1, 3)):
                serv, _ = Servicio.objects.get_or_create(
                    nombre=f'{tipo.nombre} - Sesión {i+1}',
                    defaults={
                        'tipo_servicio': tipo,
                        'duracion_minutos': random.choice([30, 45, 60, 90]),
                        'precio_base': Decimal(random.randint(3000, 15000)),
                        'activo': True,
                    }
                )
                servicios.append(serv)
        return servicios

    def seed_turnos(self, pacientes, empleados, servicios):
        turnos = []
        estados = [e for e in EstadoTurno if e != EstadoTurno.CANCELADO]
        for _ in range(40):
            paciente = random.choice(pacientes)
            empleado = random.choice(empleados)
            servicio = random.choice(servicios)
            fecha = fake.date_between(start_date='-30d', end_date='+30d')
            hora_inicio = time(random.randint(8, 17), random.choice([0, 30]))
            duracion = servicio.duracion_minutos
            hora_fin = time(
                (hora_inicio.hour * 60 + hora_inicio.minute + duracion) // 60,
                (hora_inicio.hour * 60 + hora_inicio.minute + duracion) % 60
            )
            turno, _ = Turno.objects.get_or_create(
                paciente=paciente,
                profesional=empleado,
                servicio=servicio,
                fecha=fecha,
                hora_inicio=hora_inicio,
                defaults={
                    'hora_fin': hora_fin,
                    'estado': random.choice(estados),
                    'observaciones': fake.text(max_nb_chars=100) if random.random() > 0.7 else '',
                }
            )
            turnos.append(turno)
        return turnos

    def seed_asistencias(self, turnos):
        asistencias = []
        for turno in turnos:
            if turno.estado in [EstadoTurno.REALIZADO, EstadoTurno.CONFIRMADO]:
                asis, _ = AsistenciaPaciente.objects.get_or_create(
                    turno=turno,
                    defaults={
                        'presente': turno.estado == EstadoTurno.REALIZADO,
                        'observaciones': fake.text(max_nb_chars=100) if random.random() > 0.8 else '',
                    }
                )
                asistencias.append(asis)
        return asistencias

    def seed_planes_tratamiento(self, pacientes, usuarios):
        planes = []
        for paciente in random.sample(pacientes, min(len(pacientes), 10)):
            plan, _ = PlanTratamiento.objects.get_or_create(
                paciente=paciente,
                defaults={
                    'nombre': f'Plan {fake.word().capitalize()} {fake.word().capitalize()}',
                    'descripcion': fake.text(max_nb_chars=300),
                    'fecha_inicio': fake.date_between(start_date='-6m', end_date='today'),
                    'fecha_fin': fake.date_between(start_date='today', end_date='+6m'),
                    'observaciones': fake.text(max_nb_chars=300),
                    'activo': True,
                }
            )
            planes.append(plan)
        return planes

    def seed_objetivos(self, planes):
        objetivos = []
        for plan in planes:
            for i in range(random.randint(1, 4)):
                obj, _ = ObjetivoTratamiento.objects.get_or_create(
                    plan_tratamiento=plan,
                    descripcion=f'Objetivo {i+1}: {fake.sentence()}',
                    defaults={
                        'cumplido': random.random() > 0.7,
                        'activo': True,
                    }
                )
                objetivos.append(obj)
        return objetivos

    def seed_actividades(self, planes, servicios, empleados):
        actividades = []
        for plan in planes:
            for _ in range(random.randint(2, 5)):
                act, _ = ActividadPlan.objects.get_or_create(
                    plan_tratamiento=plan,
                    defaults={
                        'servicio': random.choice(servicios),
                        'descripcion': fake.text(max_nb_chars=200),
                        'frecuencia_semanal': random.randint(1, 3),
                        'activo': True,
                    }
                )
                actividades.append(act)
        return actividades

    def seed_historiales(self, pacientes, usuarios):
        historiales = []
        from empleados.models import Empleado
        empleados = list(Empleado.objects.filter(activo=True))
        for paciente in random.sample(pacientes, min(len(pacientes), 10)):
            hist, _ = HistorialMedico.objects.get_or_create(
                paciente=paciente,
                defaults={
                    'fecha': fake.date_between(start_date='-2y', end_date='today'),
                    'profesional': random.choice(empleados) if empleados else None,
                    'descripcion': fake.text(max_nb_chars=500),
                    'observaciones': fake.text(max_nb_chars=300) if random.random() > 0.5 else '',
                }
            )
            historiales.append(hist)
        return historiales

    def seed_evoluciones(self, pacientes, planes, usuarios):
        evoluciones = []
        from empleados.models import Empleado
        empleados = list(Empleado.objects.filter(activo=True))
        for paciente in random.sample(pacientes, min(len(pacientes), 8)):
            for plan in [p for p in planes if p.paciente == paciente]:
                for _ in range(random.randint(1, 3)):
                    evo, _ = EvolucionSemanal.objects.get_or_create(
                        paciente=paciente,
                        plan_tratamiento=plan,
                        defaults={
                            'fecha': fake.date_between(start_date='-2m', end_date='today'),
                            'profesional': random.choice(empleados) if empleados else None,
                            'descripcion': fake.text(max_nb_chars=400),
                        }
                    )
                    evoluciones.append(evo)
        return evoluciones

    def seed_registros(self, actividades):
        registros = []
        from empleados.models import Empleado
        empleados = list(Empleado.objects.filter(activo=True))
        for act in random.sample(actividades, min(len(actividades), 15)):
            for _ in range(random.randint(1, 4)):
                reg, _ = RegistroActividad.objects.get_or_create(
                    actividad=act,
                    defaults={
                        'paciente': act.plan_tratamiento.paciente,
                        'profesional': random.choice(empleados) if empleados else None,
                        'fecha': fake.date_between(start_date='-1m', end_date='today'),
                        'descripcion': fake.text(max_nb_chars=200) if random.random() > 0.5 else '',
                    }
                )
                registros.append(reg)
        return registros

    def seed_notas(self, pacientes, usuarios):
        notas = []
        from empleados.models import Empleado
        empleados = list(Empleado.objects.filter(activo=True))
        for paciente in random.sample(pacientes, min(len(pacientes), 10)):
            nota, _ = NotaImportante.objects.get_or_create(
                paciente=paciente,
                defaults={
                    'profesional': random.choice(empleados) if empleados else None,
                    'titulo': fake.sentence(nb_words=6),
                    'descripcion': fake.text(max_nb_chars=300),
                }
            )
            notas.append(nota)
        return notas

    def seed_facturas(self, pacientes, obras_sociales):
        facturas = []
        for i in range(25):
            paciente = random.choice(pacientes)
            factura, _ = FacturaVenta.objects.get_or_create(
                numero_factura=f'FAC-{i+1:05d}',
                defaults={
                    'paciente': paciente,
                    'obra_social': paciente.obra_social or random.choice(obras_sociales),
                    'fecha': fake.date_between(start_date='-6m', end_date='today'),
                    'estado': random.choice([e for e in EstadoFactura if e != EstadoFactura.ANULADA]),
                    'total': Decimal('0.00'),
                    'observaciones': fake.text(max_nb_chars=200) if random.random() > 0.7 else '',
                }
            )
            facturas.append(factura)
        return facturas

    def seed_detalles_factura(self, facturas, servicios):
        detalles = []
        for factura in facturas:
            for _ in range(random.randint(1, 4)):
                servicio = random.choice(servicios)
                cantidad = random.randint(1, 3)
                precio = servicio.precio_base or Decimal('0.00')
                subtotal = precio * cantidad
                det, _ = DetalleVenta.objects.get_or_create(
                    factura=factura,
                    servicio=servicio,
                    defaults={
                        'descripcion': servicio.nombre,
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'subtotal': subtotal,
                    }
                )
                detalles.append(det)
            factura.calcular_total()
            factura.save(update_fields=['subtotal', 'total'])
        return detalles

    def seed_pagos(self, facturas):
        pagos = []
        for factura in facturas:
            if factura.estado in [EstadoFactura.PAGADA, EstadoFactura.PARCIAL]:
                pagado = Decimal('0.00')
                while pagado < factura.total:
                    monto = min(factura.total - pagado, Decimal(random.randint(1000, 10000)))
                    pago, _ = Pago.objects.get_or_create(
                        factura=factura,
                        monto=monto,
                        defaults={
                            'fecha': fake.date_between(start_date=factura.fecha, end_date='today'),
                            'medio_pago': random.choice([c[0] for c in Pago.MedioPago.choices]),
                            'referencia': fake.uuid4()[:20],
                        }
                    )
                    pagos.append(pago)
                    pagado += monto
        return pagos

    def seed_categorias_producto(self):
        categorias = []
        data = [
            ('Medicamentos', 'Medicamentos y fármacos'),
            ('Material Médico', 'Insumos médicos descartables'),
            ('Equipamiento', 'Equipos y dispositivos médicos'),
            ('Higiene', 'Productos de higiene y limpieza'),
            ('Alimentos', 'Suplementos nutricionales y alimentos'),
        ]
        for nombre, desc in data:
            cat, _ = CategoriaProducto.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc, 'activo': True})
            categorias.append(cat)
        return categorias

    def seed_productos(self, categorias):
        productos = []
        for cat in categorias:
            for i in range(random.randint(5, 10)):
                prod, _ = Producto.objects.get_or_create(
                    codigo=f'{cat.nombre[:3].upper()}-{i+1:03d}',
                    defaults={
                        'nombre': f'{cat.nombre} {fake.word().capitalize()} {i+1}',
                        'descripcion': fake.text(max_nb_chars=200),
                        'categoria': cat,
                        'stock_minimo': random.randint(5, 20),
                        'stock_actual': random.randint(10, 100),
                        'precio_compra': Decimal(random.randint(500, 5000)),
                        'precio_venta': Decimal(random.randint(600, 8000)),
                        'activo': True,
                    }
                )
                productos.append(prod)
        return productos

    def seed_movimientos_stock(self, productos):
        movimientos = []
        for prod in random.sample(productos, min(len(productos), 20)):
            for _ in range(random.randint(1, 5)):
                # Solo ENTRADA y AJUSTE para evitar problemas de stock insuficiente
                tipo = random.choice(['ENTRADA', 'AJUSTE'])
                cantidad = random.randint(1, 20)
                stock_anterior = prod.stock_actual
                if tipo == 'ENTRADA':
                    stock_resultante = stock_anterior + cantidad
                else:  # AJUSTE
                    stock_resultante = cantidad
                mov, _ = MovimientoStock.objects.get_or_create(
                    producto=prod,
                    tipo=tipo,
                    cantidad=cantidad,
                    defaults={
                        'stock_anterior': stock_anterior,
                        'stock_resultante': stock_resultante,
                        'motivo': fake.text(max_nb_chars=100),
                        'fecha': fake.date_between(start_date='-3m', end_date='today'),
                    }
                )
                prod.stock_actual = stock_resultante
                prod.save(update_fields=['stock_actual'])
                movimientos.append(mov)
        return movimientos

    def seed_proveedores(self):
        proveedores = []
        for i in range(8):
            prov, _ = Proveedor.objects.get_or_create(
                cuit=f'30-{10000000 + i:08d}-{i}',
                defaults={
                    'razon_social': fake.company(),
                    'direccion': fake.street_address(),
                    'telefono': fake.phone_number()[:20],
                    'email': fake.company_email(),
                    'activo': True,
                }
            )
            proveedores.append(prov)
        return proveedores

    def seed_compras(self, proveedores, productos):
        compras = []
        for _ in range(15):
            proveedor = random.choice(proveedores)
            compra, _ = Compra.objects.get_or_create(
                proveedor=proveedor,
                defaults={
                    'fecha': fake.date_between(start_date='-3m', end_date='today'),
                    'numero_comprobante': f'FC-{random.randint(1000, 9999):04d}',
                    'total': Decimal('0.00'),
                    'anulada': False,
                    'observaciones': fake.text(max_nb_chars=200) if random.random() > 0.7 else '',
                }
            )
            compras.append(compra)
        return compras

    def seed_detalles_compra(self, compras, productos):
        detalles = []
        for compra in compras:
            for _ in range(random.randint(1, 5)):
                prod = random.choice(productos)
                cantidad = random.randint(1, 10)
                precio = prod.precio_compra
                subtotal = precio * cantidad
                det, _ = DetalleCompra.objects.get_or_create(
                    compra=compra,
                    producto=prod,
                    defaults={
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'subtotal': subtotal,
                    }
                )
                detalles.append(det)
            compra.total = sum(d.subtotal for d in compra.detalles.all())
            compra.save(update_fields=['total'])
        return detalles

    def seed_tipos_gasto(self):
        tipos = []
        data = [
            ('Servicios', 'Luz, gas, agua, internet'),
            ('Alquiler', 'Alquiler del inmueble'),
            ('Mantenimiento', 'Reparaciones y mantenimiento'),
            ('Insumos', 'Compra de insumos médicos'),
            ('Capacitación', 'Cursos y capacitaciones del personal'),
            ('Marketing', 'Publicidad y marketing'),
            ('Transporte', 'Viáticos y combustible'),
            ('Impuestos', 'Impuestos y tasas municipales'),
        ]
        for nombre, desc in data:
            tipo, _ = TipoGasto.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc, 'activo': True})
            tipos.append(tipo)
        return tipos

    def seed_gastos(self, tipos_gasto, proveedores):
        gastos = []
        for _ in range(20):
            tipo = random.choice(tipos_gasto)
            prov = random.choice(proveedores) if random.random() > 0.3 else None
            gasto, _ = Gasto.objects.get_or_create(
                concepto=f'{tipo.nombre} - {fake.word().capitalize()}',
                defaults={
                    'tipo_gasto': tipo,
                    'proveedor': prov,
                    'fecha': fake.date_between(start_date='-3m', end_date='today'),
                    'monto': Decimal(random.randint(5000, 100000)),
                    'numero_comprobante': f'G-{random.randint(1000, 9999):04d}',
                    'anulado': False,
                    'observaciones': fake.text(max_nb_chars=200) if random.random() > 0.7 else '',
                }
            )
            gastos.append(gasto)
        return gastos

    def seed_documentos(self, personas):
        documentos = []
        for persona in random.sample(personas, min(len(personas), 20)):
            for _ in range(random.randint(1, 3)):
                doc, _ = Documento.objects.get_or_create(
                    persona=persona,
                    tipo=random.choice([c[0] for c in Documento.TipoDocumento.choices]),
                    nombre=f'{fake.word().capitalize()} {fake.word().capitalize()}',
                    defaults={
                        'archivo': '',
                        'descripcion': fake.text(max_nb_chars=200),
                        'fecha_documento': fake.date_between(start_date='-2y', end_date='today'),
                        'fecha_vencimiento': fake.future_date(end_date='+2y') if random.random() > 0.5 else None,
                        'activo': True,
                    }
                )
                documentos.append(doc)
        return documentos