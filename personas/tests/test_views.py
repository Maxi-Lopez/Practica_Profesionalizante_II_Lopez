import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from personas.models import Persona, Pais, Provincia, Localidad


@pytest.mark.django_db
class TestPersonaViews:
    def setup_method(self):
        """Configuración común para los tests."""
        self.client = APIClient()
        self.pais = Pais.objects.create(nombre="Argentina", activo=True)
        self.provincia = Provincia.objects.create(nombre="Córdoba", pais=self.pais, activo=True)
        self.localidad = Localidad.objects.create(nombre="Río Cuarto", provincia=self.provincia, codigo_postal="5800", activo=True)
        self.persona = Persona.objects.create(
            nombre="Test",
            apellido="User",
            dni="12345678",
            localidad=self.localidad,
            activo=True
        )

    def test_get_persona_get_devuelve_200_publico(self):
        """Test 3: Verificar que GET /api/personas/persona-get/ devuelva 200 OK (público)."""
        url = reverse('persona-get-api-list')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # La respuesta es una lista directa (sin paginación en este ViewSet)
        assert isinstance(response.data, list)
        assert len(response.data) >= 1

    def test_get_persona_get_detalle_devuelve_200(self):
        """Verificar que GET /api/personas/persona-get/{id}/ devuelva 200 OK."""
        url = reverse('persona-get-api-detail', kwargs={'pk': self.persona.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'Test'
        assert response.data['apellido'] == 'User'
        assert response.data['dni'] == '12345678'
        assert 'localidad' in response.data

    def test_post_persona_devuelve_401_sin_autenticacion(self):
        """Test 4: Verificar que POST /api/personas/persona/ devuelva 401/403 si no hay autenticación."""
        url = reverse('persona-api-list')
        data = {
            'nombre': 'Nueva',
            'apellido': 'Persona',
            'dni': '87654321',
            'localidad': self.localidad.id,
        }
        response = self.client.post(url, data, format='json')

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_post_persona_get_devuelve_405(self):
        """Verificar que POST en endpoint de solo lectura devuelva 405."""
        url = reverse('persona-get-api-list')
        data = {
            'nombre': 'Nueva',
            'apellido': 'Persona',
            'dni': '87654321',
            'localidad': self.localidad.id,
        }
        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_filtro_busqueda_persona_get(self):
        """Verificar que la búsqueda en persona-get funcione."""
        url = reverse('persona-get-api-list')
        response = self.client.get(url, {'search': 'Test'})

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 1
        assert any(p['dni'] == '12345678' for p in response.data)

    def test_filtro_por_localidad_persona_get(self):
        """Verificar que el filtro por localidad funcione."""
        url = reverse('persona-get-api-list')
        response = self.client.get(url, {'localidad': self.localidad.id})

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 1
        assert all(p['localidad']['id'] == self.localidad.id for p in response.data)

    def test_ordenamiento_persona_get(self):
        """Verificar que el ordenamiento funcione."""
        url = reverse('persona-get-api-list')
        response = self.client.get(url, {'ordering': 'apellido'})

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        apellidos = [p['apellido'] for p in response.data]
        assert apellidos == sorted(apellidos)