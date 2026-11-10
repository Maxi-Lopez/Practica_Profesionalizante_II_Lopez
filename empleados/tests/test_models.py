import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from model_bakery import baker


@pytest.mark.django_db
class TestEmpleadoModel:
    """Tests de validación del modelo Empleado."""

    def setup_method(self):
        """Configuración común para los tests."""
        from personas.models import Persona, Pais, Provincia, Localidad
        from empleados.models import Empleado, Rol

        self.Persona = Persona
        self.Empleado = Empleado
        self.Rol = Rol

        self.pais = baker.make(Pais, nombre="Argentina")
        self.provincia = baker.make(Provincia, nombre="Córdoba", pais=self.pais)
        self.localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=self.provincia)
        self.rol = baker.make(Rol, nombre="Psicólogo", activo=True)

    def test_empleado_matricula_duplicada_lanza_error(self):
        """
        Test 1: Verificar que un Empleado no se pueda crear con una matrícula duplicada.
        """
        persona1 = baker.make(
            self.Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        baker.make(self.Empleado, persona=persona1, matricula="MAT-001", activo=True)

        persona2 = baker.make(
            self.Persona, nombre="Pedro", apellido="Gómez", dni="87654321", localidad=self.localidad
        )
        empleado2 = self.Empleado(persona=persona2, matricula="MAT-001", activo=True)

        with pytest.raises(ValidationError):
            empleado2.full_clean()

    def test_empleado_dni_duplicado_lanza_error(self):
        """
        Test 2: Verificar que un Empleado no se pueda crear con un DNI duplicado.
        El DNI es único a nivel de Persona (constraint de BD).
        """
        from django.db import IntegrityError

        persona1 = baker.make(
            self.Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        baker.make(self.Empleado, persona=persona1, matricula="MAT-001", activo=True)

        # Intentar crear otra Persona con el mismo DNI debe fallar en la BD
        with pytest.raises(IntegrityError):
            baker.make(
                self.Persona, nombre="Pedro", apellido="Gómez", dni="12345678", localidad=self.localidad
            )

    def test_empleado_fecha_baja_anterior_a_ingreso_lanza_error(self):
        """
        Test 3: Verificar que fecha_baja no pueda ser anterior a fecha_ingreso.
        """
        persona = baker.make(
            self.Persona, nombre="Ana", apellido="Martínez", dni="11223344", localidad=self.localidad
        )
        empleado = self.Empleado(
            persona=persona,
            matricula="MAT-003",
            fecha_ingreso=timezone.now().date(),
            fecha_baja=timezone.now().date() - timezone.timedelta(days=10),
            activo=True
        )

        with pytest.raises(ValidationError):
            empleado.full_clean()

    def test_empleado_baja_logica_funciona(self):
        """
        Test 4: Verificar que la baja lógica (activo=False) funciona correctamente.
        """
        persona = baker.make(
            self.Persona, nombre="Carlos", apellido="López", dni="55667788", localidad=self.localidad
        )
        empleado = baker.make(self.Empleado, persona=persona, matricula="MAT-004", activo=True)

        assert empleado.activo is True
        empleado.activo = False
        empleado.save()

        empleado.refresh_from_db()
        assert empleado.activo is False

    def test_empleado_creacion_exitosa(self):
        """
        Test 5: Verificar que un empleado se crea correctamente con datos válidos.
        """
        persona = baker.make(
            self.Persona, nombre="María", apellido="García", dni="99887766", localidad=self.localidad
        )
        empleado = baker.make(
            self.Empleado,
            persona=persona,
            matricula="MAT-005",
            fecha_ingreso=timezone.now().date(),
            horas_semanales=40,
            activo=True
        )

        assert empleado.id is not None
        assert empleado.persona.nombre == "María"
        assert empleado.matricula == "MAT-005"
        assert empleado.horas_semanales == 40
        assert empleado.activo is True

    def test_empleado_roles_funcionan(self):
        """
        Test 6: Verificar que la relación Empleado-Rol funciona correctamente.
        """
        from empleados.models import EmpleadoRol

        persona = baker.make(
            self.Persona, nombre="Lucía", apellido="Fernández", dni="44332211", localidad=self.localidad
        )
        empleado = baker.make(self.Empleado, persona=persona, matricula="MAT-006", activo=True)

        rol2 = baker.make(self.Rol, nombre="Supervisor", activo=True)
        baker.make("empleados.EmpleadoRol", empleado=empleado, rol=self.rol, activo=True)
        baker.make("empleados.EmpleadoRol", empleado=empleado, rol=rol2, activo=True)

        assert empleado.roles.filter(activo=True).count() == 2
        roles_nombres = set(empleado.roles.filter(activo=True).values_list('rol__nombre', flat=True))
        assert roles_nombres == {"Psicólogo", "Supervisor"}

    def test_empleado_horarios_funcionan(self):
        """
        Test 7: Verificar que la relación Empleado-Horario funciona correctamente.
        """
        from empleados.models import HorarioEmpleado

        persona = baker.make(
            self.Persona, nombre="Roberto", apellido="Sosa", dni="11998877", localidad=self.localidad
        )
        empleado = baker.make(self.Empleado, persona=persona, matricula="MAT-007", activo=True)

        baker.make(
            HorarioEmpleado,
            empleado=empleado,
            dia_semana=HorarioEmpleado.DiaSemana.LUNES,
            hora_inicio="08:00",
            hora_fin="12:00",
            activo=True
        )
        baker.make(
            HorarioEmpleado,
            empleado=empleado,
            dia_semana=HorarioEmpleado.DiaSemana.MIERCOLES,
            hora_inicio="14:00",
            hora_fin="18:00",
            activo=True
        )

        assert empleado.horarios.filter(activo=True).count() == 2

    def test_empleado_str(self):
        """
        Test 8: Verificar la representación en string del modelo.
        """
        persona = baker.make(
            self.Persona, nombre="Test", apellido="User", dni="11111111", localidad=self.localidad
        )
        empleado = baker.make(self.Empleado, persona=persona, matricula="MAT-008", activo=True)

        assert str(empleado) == "User, Test - DNI 11111111"