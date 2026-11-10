import pytest
from decimal import Decimal
from model_bakery import baker


@pytest.mark.django_db
class TestEmpleadoSerializer:
    """Tests de validación del serializer de Empleado."""

    def setup_method(self):
        """Configuración común para los tests."""
        from personas.models import Persona, Pais, Provincia, Localidad
        from empleados.models import Rol

        self.pais = baker.make(Pais, nombre="Argentina")
        self.provincia = baker.make(Provincia, nombre="Córdoba", pais=self.pais)
        self.localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=self.provincia)
        self.rol = baker.make(Rol, nombre="Psicólogo", activo=True)

    def test_serializer_valida_campos_obligatorios(self):
        """
        Test: Verificar que el serializer valide correctamente los campos obligatorios.
        """
        from empleados.serializers import EmpleadoSerializer
        from personas.models import Persona

        persona = baker.make(
            Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        
        data = {
            'persona': persona.pk,
            'matricula': 'MAT-001',
            'fecha_ingreso': '2024-01-15',
            'horas_semanales': 40,
        }
        serializer = EmpleadoSerializer(data=data)
        assert serializer.is_valid(), f"Errores: {serializer.errors}"

    def test_serializer_rechaza_matricula_duplicada(self):
        """
        Test: Verificar que el serializer rechace matrícula duplicada.
        """
        from empleados.serializers import EmpleadoSerializer
        from empleados.models import Empleado
        from personas.models import Persona

        persona1 = baker.make(
            Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        baker.make(Empleado, persona=persona1, matricula="MAT-001", activo=True)

        persona2 = baker.make(
            Persona, nombre="Pedro", apellido="Gómez", dni="87654321", localidad=self.localidad
        )

        data = {
            'persona': persona2.pk,
            'matricula': 'MAT-001',  # Duplicada
            'fecha_ingreso': '2024-01-15',
            'horas_semanales': 40,
        }
        serializer = EmpleadoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'matricula' in serializer.errors

    def test_serializer_crea_empleado_correctamente(self):
        """
        Test: Verificar que el serializer cree un empleado correctamente.
        """
        from empleados.serializers import EmpleadoSerializer
        from personas.models import Persona

        persona = baker.make(
            Persona, nombre="Ana", apellido="Martínez", dni="99887766", localidad=self.localidad
        )
        
        data = {
            'persona': persona.pk,
            'matricula': 'MAT-999',
            'fecha_ingreso': '2024-01-15',
            'horas_semanales': 35,
        }
        serializer = EmpleadoSerializer(data=data)
        assert serializer.is_valid(), f"Errores: {serializer.errors}"
        empleado = serializer.save()
        
        assert empleado.matricula == 'MAT-999'
        assert empleado.horas_semanales == 35
        assert empleado.persona == persona

    def test_serializer_actualiza_empleado_correctamente(self):
        """
        Test: Verificar que el serializer actualice un empleado correctamente.
        """
        from empleados.serializers import EmpleadoSerializer
        from empleados.models import Empleado
        from personas.models import Persona

        persona = baker.make(
            Persona, nombre="Original", apellido="Apellido", dni="11111111", localidad=self.localidad
        )
        empleado = baker.make(Empleado, persona=persona, matricula="MAT-111", horas_semanales=40)

        data = {
            'matricula': 'MAT-111',
            'fecha_ingreso': '2020-01-01',
            'horas_semanales': 30,
        }
        serializer = EmpleadoSerializer(empleado, data=data, partial=True)
        assert serializer.is_valid(), f"Errores: {serializer.errors}"
        empleado_actualizado = serializer.save()
        
        assert empleado_actualizado.horas_semanales == 30

    def test_empleado_list_serializer_incluye_nested(self):
        """
        Test: Verificar que EmpleadoListSerializer incluya persona, roles y horarios anidados.
        """
        from empleados.serializers import EmpleadoListSerializer
        from empleados.models import Empleado, EmpleadoRol, HorarioEmpleado, Rol
        from personas.models import Persona

        persona = baker.make(
            Persona, nombre="Test", apellido="User", dni="11111111", localidad=self.localidad
        )
        empleado = baker.make(Empleado, persona=persona, matricula="MAT-222", activo=True)
        
        rol = baker.make(Rol, nombre="Kinesiólogo", activo=True)
        baker.make("empleados.EmpleadoRol", empleado=empleado, rol=self.rol, activo=True)
        baker.make("empleados.EmpleadoRol", empleado=empleado, rol=rol, activo=True)
        
        baker.make(
            HorarioEmpleado,
            empleado=empleado,
            dia_semana=HorarioEmpleado.DiaSemana.LUNES,
            hora_inicio="08:00",
            hora_fin="12:00",
            activo=True
        )

        serializer = EmpleadoListSerializer(empleado)
        data = serializer.data

        assert 'persona' in data
        assert data['persona']['nombre'] == 'Test'
        assert 'roles' in data
        assert len(data['roles']) == 2
        assert 'horarios' in data
        assert len(data['horarios']) == 1

    def test_serializer_valida_horas_semanales_negativas(self):
        """
        Test: Verificar que el serializer rechace horas_semanales negativas.
        """
        from empleados.serializers import EmpleadoSerializer
        from personas.models import Persona

        persona = baker.make(
            Persona, nombre="Test", apellido="User", dni="22222222", localidad=self.localidad
        )

        data = {
            'persona': persona.pk,
            'matricula': 'MAT-333',
            'fecha_ingreso': '2024-01-15',
            'horas_semanales': -5,  # Negativo
        }
        serializer = EmpleadoSerializer(data=data)
        assert not serializer.is_valid()
        assert 'horas_semanales' in serializer.errors