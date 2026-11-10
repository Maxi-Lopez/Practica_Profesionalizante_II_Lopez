import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker


@pytest.mark.django_db
class TestAreasViewsHTML:
    """Tests de autenticación y permisos en vistas HTML de Áreas."""

    def setup_method(self):
        """Configuración común para los tests."""
        self.client = APIClient()
        
        from pacientes.models import AreaInterdisciplinaria
        
        self.AreaInterdisciplinaria = AreaInterdisciplinaria

        # Usuario admin
        from usuarios.models import Usuario
        self.admin_user = Usuario.objects.create_user(
            username="admin_test",
            password="test1234",
            email="admin@test.com",
            is_staff=True,
            is_superuser=True,
            rol="admin"
        )

        # Usuario profesional
        self.profesional_user = Usuario.objects.create_user(
            username="prof_test",
            password="test1234",
            email="prof@test.com",
            rol="profesional"
        )

        # Datos base para área
        self.area = baker.make(self.AreaInterdisciplinaria, nombre="psicologia", activo=True)

    def test_areas_list_sin_login_redirige_a_login(self):
        """
        Test: GET /areas/ sin login debe redirigir a login (302).
        """
        url = reverse('areas_list')
        response = self.client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_areas_list_con_login_admin_retorna_200(self):
        """
        Test: GET /areas/ con login admin debe retornar 200.
        """
        self.client.force_login(self.admin_user)
        url = reverse('areas_list')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_area_create_sin_login_redirige_a_login(self):
        """
        Test: GET /areas/crear/ sin login debe redirigir a login.
        """
        url = reverse('area_create')
        response = self.client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_area_create_con_admin_retorna_200(self):
        """
        Test: GET /areas/crear/ con admin debe retornar 200.
        """
        self.client.force_login(self.admin_user)
        url = reverse('area_create')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_area_create_post_admin_crea_area(self):
        """
        Test: POST /areas/crear/ con admin crea área correctamente.
        """
        self.client.force_login(self.admin_user)
        
        url = reverse('area_create')
        data = {
            'nombre': 'kinesiologia',
            'descripcion': 'Área de kinesiología',
        }
        response = self.client.post(url, data)
        
        assert response.status_code == 302  # Redirect after success
        assert self.AreaInterdisciplinaria.objects.filter(nombre='kinesiologia').exists()

    def test_area_update_con_admin_retorna_200(self):
        """
        Test: GET /areas/editar/<pk>/ con admin debe retornar 200.
        """
        self.client.force_login(self.admin_user)
        url = reverse('area_update', kwargs={'pk': self.area.pk})
        response = self.client.get(url)
        assert response.status_code == 200

    def test_area_update_post_admin_actualiza_area(self):
        """
        Test: POST /areas/editar/<pk>/ con admin actualiza área.
        """
        self.client.force_login(self.admin_user)
        
        url = reverse('area_update', kwargs={'pk': self.area.pk})
        data = {
            'nombre': 'trabajo_social',
            'descripcion': 'Área de trabajo social actualizada',
        }
        response = self.client.post(url, data)
        
        assert response.status_code == 302
        self.area.refresh_from_db()
        assert self.area.nombre == 'trabajo_social'

    def test_area_delete_post_admin_da_de_baja(self):
        """
        Test: POST /areas/eliminar/<pk>/ con admin da de baja al área (baja lógica).
        """
        self.client.force_login(self.admin_user)
        
        # Crear un área específica para este test
        area_test = baker.make(self.AreaInterdisciplinaria, nombre="nutricion", activo=True)
        
        url = reverse('area_delete', kwargs={'pk': area_test.pk})
        response = self.client.post(url)
        
        assert response.status_code == 302
        area_test.refresh_from_db()
        assert area_test.activo is False