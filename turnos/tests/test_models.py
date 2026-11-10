import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_bakery import baker


@pytest.mark.django_db
class TestTurnoModel:
    """Tests de validación del modelo Turno."""

    def setup_method(self):
        """Configuración común para los tests."""
        # Crear datos base: paciente, profesional, servicio
        from personas.models import Persona, Pais, Provincia, Localidad
        from pacientes.models import Paciente
        from empleados.models import Empleado, Rol
        from servicios.models import Servicio, TipoServicio

        self.pais = baker.make(Pais, nombre="Argentina")
        self.provincia = baker.make(Provincia, nombre="Córdoba", pais=self.pais)
        self.localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=self.provincia)

        # Persona y Paciente
        self.persona_paciente = baker.make(
            Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        self.paciente = baker.make(Paciente, persona=self.persona_paciente)

        # Rol y Profesional
        self.rol = baker.make(Rol, nombre="Psicólogo")
        self.persona_prof = baker.make(
            Persona, nombre="Ana", apellido="García", dni="87654321", localidad=self.localidad
        )
        self.profesional = baker.make(Empleado, persona=self.persona_prof)
        baker.make(
            "empleados.EmpleadoRol",
            empleado=self.profesional,
            rol=self.rol,
            activo=True,
        )

        # TipoServicio y Servicio
        self.tipo_servicio = baker.make(TipoServicio, nombre="Terapia")
        self.servicio = baker.make(Servicio, tipo_servicio=self.tipo_servicio, nombre="Terapia individual")

    def test_turno_hora_fin_menor_que_inicio_lanza_error(self):
        """
        Test 1: Verificar que un Turno con hora_fin <= hora_inicio lance ValidationError.
        Arrange: Crear un Turno con hora_fin anterior a hora_inicio (usando prepare para no guardar).
        Act: Llamar a full_clean().
        Assert: Se lanza ValidationError con mensaje en campo hora_fin.
        """
        turno = baker.prepare(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=timezone.now().date(),
            hora_inicio="10:00",
            hora_fin="09:30",  # Anterior a hora_inicio
        )

        with pytest.raises(ValidationError) as exc_info:
            turno.full_clean()

        assert "hora_fin" in exc_info.value.message_dict
        assert "posterior" in str(exc_info.value).lower()

    def test_turno_hora_fin_igual_a_inicio_lanza_error(self):
        """
        Verificar que un Turno con hora_fin igual a hora_inicio lance ValidationError.
        """
        turno = baker.prepare(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=timezone.now().date(),
            hora_inicio="10:00",
            hora_fin="10:00",  # Igual a hora_inicio
        )

        with pytest.raises(ValidationError) as exc_info:
            turno.full_clean()

        assert "hora_fin" in exc_info.value.message_dict

    def test_turno_solapamiento_mismo_profesional_lanza_error(self):
        """
        Test 2: Verificar que no se pueda crear un Turno que se solape
        con otro turno del mismo profesional en la misma fecha.
        Arrange: Crear un Turno existente de 10:00-11:00 con profesional X.
        Act: Intentar crear otro Turno de 10:30-11:30 con el mismo profesional X.
        Assert: Se lanza ValidationError indicando solapamiento.
        """
        fecha_hoy = timezone.now().date()

        # Turno existente: 10:00 - 11:00
        baker.make(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=fecha_hoy,
            hora_inicio="10:00",
            hora_fin="11:00",
            estado="CONFIRMADO",
        )

        # Nuevo turno que se solapa: 10:30 - 11:30 (usar prepare)
        turno_solapado = baker.prepare(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=fecha_hoy,
            hora_inicio="10:30",
            hora_fin="11:30",
        )

        with pytest.raises(ValidationError) as exc_info:
            turno_solapado.full_clean()

        assert "hora_inicio" in exc_info.value.message_dict
        assert "ya tiene un turno" in str(exc_info.value)

    def test_turno_sin_solapamiento_se_crea_correctamente(self):
        """
        Verificar que un Turno en horario distinto al existente se crea correctamente.
        """
        fecha_hoy = timezone.now().date()

        # Turno existente: 10:00 - 11:00
        baker.make(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=fecha_hoy,
            hora_inicio="10:00",
            hora_fin="11:00",
            estado="CONFIRMADO",
        )

        # Nuevo turno SIN solapamiento: 11:00 - 12:00 (justo al terminar el anterior)
        turno_ok = baker.prepare(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=fecha_hoy,
            hora_inicio="11:00",
            hora_fin="12:00",
        )

        # No debe lanzar excepción
        turno_ok.full_clean()
        # Guardar para verificar que se persiste
        turno_ok.save()
        assert turno_ok.pk is not None

    def test_turno_distinto_profesional_mismo_horario_se_crea_correctamente(self):
        """
        Verificar que el mismo horario con distinto profesional NO se considera solapamiento.
        """
        from personas.models import Persona
        from empleados.models import Empleado
        fecha_hoy = timezone.now().date()

        # Crear segundo profesional
        persona_prof2 = baker.make(
            Persona, nombre="Carlos", apellido="López", dni="11223344", localidad=self.localidad
        )
        profesional2 = baker.make(Empleado, persona=persona_prof2)
        baker.make(
            "empleados.EmpleadoRol",
            empleado=profesional2,
            rol=self.rol,
            activo=True,
        )

        # Turno existente con profesional 1: 10:00 - 11:00
        baker.make(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=self.profesional,
            servicio=self.servicio,
            fecha=fecha_hoy,
            hora_inicio="10:00",
            hora_fin="11:00",
            estado="CONFIRMADO",
        )

        # Mismo horario con profesional 2
        turno_ok = baker.prepare(
            "turnos.Turno",
            paciente=self.paciente,
            profesional=profesional2,
            servicio=self.servicio,
            fecha=fecha_hoy,
            hora_inicio="10:00",
            hora_fin="11:00",
        )

        # No debe lanzar excepción
        turno_ok.full_clean()
        turno_ok.save()
        assert turno_ok.pk is not None