import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPacienteViewsAuth:
    """Tests de autenticación en vistas de Pacientes."""

    def setup_method(self):
        """Configuración común para los tests."""
        self.client = APIClient()

    def test_get_pacientes_sin_token_retorna_401(self):
        """
        Test 3: Verificar que GET /api/pacientes/paciente/ sin token retorne 401.
        Arrange: Cliente API sin autenticación.
        Act: GET al endpoint de listado de pacientes.
        Assert: Status code 401 Unauthorized.
        """
        url = reverse("paciente-api-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_pacientes_con_usuario_autenticado_retorna_200(self):
        """
        Verificar que GET /api/pacientes/paciente/ con usuario autenticado retorne 200.
        """
        from usuarios.models import Usuario

        admin_user = Usuario.objects.create_user(
            username="admin_test",
            password="test1234",
            email="admin@test.com",
            is_staff=True,
            is_superuser=True,
        )
        # Usar force_authenticate para evitar problemas con JWT
        self.client.force_authenticate(user=admin_user)

        url = reverse("paciente-api-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_post_pacientes_sin_token_retorna_401(self):
        """
        Verificar que POST /api/pacientes/paciente/ sin token retorne 401.
        """
        from personas.models import Pais, Provincia, Localidad
        from model_bakery import baker

        pais = baker.make(Pais, nombre="Argentina")
        provincia = baker.make(Provincia, nombre="Córdoba", pais=pais)
        localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=provincia)

        url = reverse("paciente-api-list")
        data = {
            "persona": {
                "nombre": "Nuevo",
                "apellido": "Paciente",
                "dni": "99887766",
                "localidad": localidad.id,
            },
            "historia_clinica": "HC-001",
        }
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED