from django.urls import path
from .views import (
    HomeView,
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    PacientesListView,
    TurnosListView,
    TratamientosListView,
    EmpleadosListView,
    ServiciosListView,
    FacturacionListView,
    InventarioListView,
    ComprasListView,
    DocumentosListView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Listados (requieren login)
    path('pacientes/', PacientesListView.as_view(), name='pacientes_list'),
    path('turnos/', TurnosListView.as_view(), name='turnos_list'),
    path('tratamientos/', TratamientosListView.as_view(), name='tratamientos_list'),
    path('empleados/', EmpleadosListView.as_view(), name='empleados_list'),
    path('servicios/', ServiciosListView.as_view(), name='servicios_list'),
    path('facturacion/', FacturacionListView.as_view(), name='facturacion_list'),
    path('inventario/', InventarioListView.as_view(), name='inventario_list'),
    path('compras/', ComprasListView.as_view(), name='compras_list'),
    path('documentos/', DocumentosListView.as_view(), name='documentos_list'),
]