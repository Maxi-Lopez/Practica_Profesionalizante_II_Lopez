"""Fixtures compartidas para todos los tests del proyecto."""
import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Cliente DRF sin autenticación."""
    return APIClient()


@pytest.fixture
def usuario_admin(db):
    """Usuario administrador de prueba."""
    from usuarios.models import Usuario
    return Usuario.objects.create_user(
        username="admin_test",
        password="test1234",
        email="admin@test.com",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def api_client_admin(api_client, usuario_admin):
    """Cliente DRF autenticado como admin (JWT)."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(usuario_admin)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def paciente_base(db):
    """Paciente de prueba con Persona, País, Provincia y Localidad asociados."""
    from personas.models import Persona, Pais, Provincia, Localidad
    from pacientes.models import Paciente

    pais = baker.make(Pais, nombre="Argentina")
    provincia = baker.make(Provincia, nombre="Córdoba", pais=pais)
    localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=provincia)
    persona = baker.make(
        Persona,
        nombre="Juan",
        apellido="Pérez",
        dni="12345678",
        localidad=localidad,
    )
    return baker.make(Paciente, persona=persona)