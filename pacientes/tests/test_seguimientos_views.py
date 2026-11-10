import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker


@pytest.mark.django_db
class TestSeguimientosViewsHTML:
    """Tests de autenticación y permisos en vistas HTML de Seguimientos."""

    def setup_method(self):
        """Configuración común para los tests."""
        self.client = APIClient()
        
        from personas.models import Persona, Pais, Provincia, Localidad
        from pacientes.models import Paciente, AreaInterdisciplinaria, SeguimientoTrimestral
        from empleados.models import Empleado, Rol
        
        self.pais = baker.make(Pais, nombre="Argentina")
        self.provincia = baker.make(Provincia, nombre="Córdoba", pais=self.pais)
        self.localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=self.provincia)
        self.rol = baker.make(Rol, nombre="Psicólogo", activo=True)

        self.Paciente = Paciente
        self.AreaInterdisciplinaria = AreaInterdisciplinaria
        self.SeguimientoTrimestral = SeguimientoTrimestral
        self.Empleado = Empleado

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

        # Datos base
        self.persona = baker.make(
            Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        self.paciente = baker.make(Paciente, persona=self.persona)
        self.area = baker.make(AreaInterdisciplinaria, nombre="psicologia", activo=True)
        self.seguimiento = baker.make(self.SeguimientoTrimestral, paciente=self.paciente, area=self.area, fecha="2024-01-15", observaciones="Seguimiento de prueba", activo=True)

    def test_seguimientos_list_sin_login_redirige_a_login(self):
        """
        Test: GET /seguimientos/ sin login debe redirigir a login (302).
        """
        url = reverse('seguimientos_list')
        response = self.client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_seguimientos_list_con_login_admin_retorna_200(self):
        """
        Test: GET /seguimientos/ con login admin debe retornar 200.
        """
        self.client.force_login(self.admin_user)
        url = reverse('seguimientos_list')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_seguimiento_create_sin_login_redirige_a_login(self):
        """
        Test: GET /seguimientos/crear/ sin login debe redirigir a login.
        """
        url = reverse('seguimiento_create')
        response = self.client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_seguimiento_create_con_admin_retorna_200(self):
        """
        Test: GET /seguimientos/crear/ con admin debe retornar 200.
        """
        self.client.force_login(self.admin_user)
        url = reverse('seguimiento_create')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_seguimiento_create_post_admin_crea_seguimiento(self):
        """
        Test: POST /seguimientos/crear/ con admin crea seguimiento correctamente.
        """
        self.client.force_login(self.admin_user)
        
        url = reverse('seguimiento_create')
        data = {
            'paciente': self.paciente.pk,
            'area': self.area.pk,
            'fecha': '2024-01-15',
            'observaciones': 'Nuevo seguimiento de prueba',
            'es_intervencion_mensual': False,
        }
        response = self.client.post(url, data)
        
        assert response.status_code == 302  # Redirect after success
        assert self.SeguimientoTrimestral.objects.filter(observaciones='Nuevo seguimiento de prueba').exists()

    def test_seguimiento_update_con_admin_retorna_200(self):
        """
        Test: GET /seguimientos/editar/<pk>/ con admin debe retornar 200.
        """
        self.client.force_login(self.admin_user)
        url = reverse('seguimiento_update', kwargs={'pk': self.seguimiento.pk})
        response = self.client.get(url)
        assert response.status_code == 200

    def test_seguimiento_update_post_admin_actualiza_seguimiento(self):
        """
        Test: POST /seguimientos/editar/<pk>/ con admin actualiza seguimiento.
        """
        self.client.force_login(self.admin_user)
        
        url = reverse('seguimiento_update', kwargs={'pk': self.seguimiento.pk})
        data = {
            'paciente': self.paciente.pk,
            'area': self.area.pk,
            'fecha': '2024-01-15',
            'observaciones': 'Seguimiento actualizado',
            'es_intervencion_mensual': False,
        }
        response = self.client.post(url, data)
        
        assert response.status_code == 302
        self.seguimiento.refresh_from_db()
        assert self.seguimiento.observaciones == 'Seguimiento actualizado'

    def test_seguimiento_delete_post_admin_da_de_baja(self):
        """
        Test: POST /seguimientos/eliminar/<pk>/ con admin da de baja al seguimiento (baja lógica).
        """
        self.client.force_login(self.admin_user)
        
        # Crear un seguimiento específico para este test
        seguimiento_test = baker.make(self.SeguimientoTrimestral, paciente=self.paciente, area=self.area, fecha="2024-01-15", observaciones="Test Delete", activo=True)
        
        url = reverse('seguimiento_delete', kwargs={'pk': seguimiento_test.pk})
        response = self.client.post(url)
        
        assert response.status_code == 302
        seguimiento_test.refresh_from_db()
        assert seguimiento_test.activo is False