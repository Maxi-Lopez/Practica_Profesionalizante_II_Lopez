import pytest
from django.core.exceptions import ValidationError
from personas.models import Persona, Pais, Provincia, Localidad
from personas.serializers import PersonaSerializer, PersonaListSerializer


@pytest.mark.django_db
class TestPersonaSerializer:
    def setup_method(self):
        """Configuración común para los tests."""
        self.pais = Pais.objects.create(nombre="Argentina", activo=True)
        self.provincia = Provincia.objects.create(nombre="Córdoba", pais=self.pais, activo=True)
        self.localidad = Localidad.objects.create(nombre="Río Cuarto", provincia=self.provincia, codigo_postal="5800", activo=True)

    def test_serializer_valida_campos_obligatorios(self):
        """Test 2: Verificar que el PersonaSerializer valide correctamente los campos obligatorios."""
        data = {
            'nombre': 'Ana',
            'apellido': 'Martínez',
            'dni': '99887766',
            'localidad': self.localidad.id,
        }
        serializer = PersonaSerializer(data=data)
        assert serializer.is_valid(), f"Errores: {serializer.errors}"

    def test_serializer_rechaza_nombre_faltante(self):
        """Verificar que el serializer rechace datos sin nombre."""
        data = {
            'apellido': 'Martínez',
            'dni': '99887766',
            'localidad': self.localidad.id,
        }
        serializer = PersonaSerializer(data=data)
        assert not serializer.is_valid()
        assert 'nombre' in serializer.errors

    def test_serializer_rechaza_apellido_faltante(self):
        """Verificar que el serializer rechace datos sin apellido."""
        data = {
            'nombre': 'Ana',
            'dni': '99887766',
            'localidad': self.localidad.id,
        }
        serializer = PersonaSerializer(data=data)
        assert not serializer.is_valid()
        assert 'apellido' in serializer.errors

    def test_serializer_rechaza_dni_faltante(self):
        """Verificar que el serializer rechace datos sin DNI."""
        data = {
            'nombre': 'Ana',
            'apellido': 'Martínez',
            'localidad': self.localidad.id,
        }
        serializer = PersonaSerializer(data=data)
        assert not serializer.is_valid()
        assert 'dni' in serializer.errors

    def test_serializer_rechaza_localidad_faltante(self):
        """Verificar que el serializer rechace datos sin localidad."""
        data = {
            'nombre': 'Ana',
            'apellido': 'Martínez',
            'dni': '99887766',
        }
        serializer = PersonaSerializer(data=data)
        assert not serializer.is_valid()
        assert 'localidad' in serializer.errors

    def test_serializer_rechaza_dni_duplicado(self):
        """Verificar que el serializer rechace DNI duplicado."""
        Persona.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            localidad=self.localidad,
            activo=True
        )

        data = {
            'nombre': 'Pedro',
            'apellido': 'Gómez',
            'dni': '12345678',
            'localidad': self.localidad.id,
        }
        serializer = PersonaSerializer(data=data)
        assert not serializer.is_valid()
        assert 'dni' in serializer.errors

    def test_serializer_crea_persona_correctamente(self):
        """Verificar que el serializer cree una persona correctamente."""
        data = {
            'nombre': 'Lucía',
            'apellido': 'Fernández',
            'dni': '55667788',
            'localidad': self.localidad.id,
            'fecha_nacimiento': '1995-05-20',
            'direccion': 'Av. Siempre Viva 742',
        }
        serializer = PersonaSerializer(data=data)
        assert serializer.is_valid(), f"Errores: {serializer.errors}"
        persona = serializer.save()
        assert persona.nombre == 'Lucía'
        assert persona.apellido == 'Fernández'
        assert persona.dni == '55667788'
        assert persona.localidad == self.localidad

    def test_serializer_actualiza_persona_correctamente(self):
        """Verificar que el serializer actualice una persona correctamente."""
        persona = Persona.objects.create(
            nombre="Original",
            apellido="Apellido",
            dni="11111111",
            localidad=self.localidad,
            activo=True
        )

        data = {
            'nombre': 'Actualizado',
            'apellido': 'Nuevo Apellido',
            'dni': '11111111',
            'localidad': self.localidad.id,
        }
        serializer = PersonaSerializer(persona, data=data, partial=True)
        assert serializer.is_valid(), f"Errores: {serializer.errors}"
        persona_actualizada = serializer.save()
        assert persona_actualizada.nombre == 'Actualizado'
        assert persona_actualizada.apellido == 'Nuevo Apellido'

    def test_persona_list_serializer_incluye_nested(self):
        """Verificar que PersonaListSerializer incluya localidad, telefonos y emails anidados."""
        persona = Persona.objects.create(
            nombre="Test",
            apellido="User",
            dni="99999999",
            localidad=self.localidad,
            activo=True
        )

        serializer = PersonaListSerializer(persona)
        data = serializer.data

        assert 'localidad' in data
        assert data['localidad']['nombre'] == 'Río Cuarto'
        assert 'telefonos' in data
        assert 'emails' in data
        assert isinstance(data['telefonos'], list)
        assert isinstance(data['emails'], list)