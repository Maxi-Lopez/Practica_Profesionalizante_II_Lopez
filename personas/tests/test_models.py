import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from personas.models import Persona, Pais, Provincia, Localidad


@pytest.mark.django_db
class TestPersonaModel:
    def test_persona_dni_duplicado_lanza_error(self):
        """Test 1: Verificar que una Persona no se pueda crear con un DNI duplicado."""
        pais = Pais.objects.create(nombre="Argentina", activo=True)
        provincia = Provincia.objects.create(nombre="Córdoba", pais=pais, activo=True)
        localidad = Localidad.objects.create(nombre="Río Cuarto", provincia=provincia, codigo_postal="5800", activo=True)

        persona1 = Persona.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            localidad=localidad,
            activo=True
        )

        persona2 = Persona(
            nombre="Pedro",
            apellido="Gómez",
            dni="12345678",
            localidad=localidad,
            activo=True
        )

        with pytest.raises(ValidationError):
            persona2.full_clean()

    def test_persona_creacion_exitosa(self):
        """Verificar que una persona se crea correctamente con datos válidos."""
        pais = Pais.objects.create(nombre="Argentina", activo=True)
        provincia = Provincia.objects.create(nombre="Córdoba", pais=pais, activo=True)
        localidad = Localidad.objects.create(nombre="Río Cuarto", provincia=provincia, codigo_postal="5800", activo=True)

        persona = Persona.objects.create(
            nombre="María",
            apellido="López",
            dni="87654321",
            fecha_nacimiento="1990-01-15",
            direccion="Calle 123",
            localidad=localidad,
            activo=True
        )

        assert persona.id is not None
        assert persona.nombre == "María"
        assert persona.apellido == "López"
        assert persona.dni == "87654321"
        assert persona.activo is True

    def test_persona_str(self):
        """Verificar la representación en string del modelo."""
        pais = Pais.objects.create(nombre="Argentina", activo=True)
        provincia = Provincia.objects.create(nombre="Córdoba", pais=pais, activo=True)
        localidad = Localidad.objects.create(nombre="Río Cuarto", provincia=provincia, codigo_postal="5800", activo=True)

        persona = Persona.objects.create(
            nombre="Carlos",
            apellido="Rodríguez",
            dni="11223344",
            localidad=localidad,
            activo=True
        )

        assert str(persona) == "Rodríguez, Carlos - DNI 11223344"