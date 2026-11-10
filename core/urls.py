from django.urls import path
from django.views.generic import RedirectView
from .views import (
    HomeView,
    CustomLoginView,
    CustomLogoutView,
    PacientesListView,
    PacienteCreateView,
    PacienteUpdateView,
    PacienteDeleteView,
    PacienteDetailView,
    PacienteLegajoPrintView,
    TurnosListView,
    TratamientosListView,
    EmpleadosListView,
    EmpleadoCreateView,
    EmpleadoUpdateView,
    EmpleadoDeleteView,
    ServiciosListView,
    FacturacionListView,
    InventarioListView,
    ComprasListView,
    DocumentosListView,
    DocumentoCreateView,
    DocumentoUpdateView,
    DocumentoDeleteView,
    SalasListView,
    SalaCreateView,
    SalaUpdateView,
    SalaDeleteView,
    AreasListView,
    AreaCreateView,
    AreaUpdateView,
    AreaDeleteView,
    DiagnosticosListView,
    DiagnosticoCreateView,
    DiagnosticoUpdateView,
    DiagnosticoDeleteView,
    SeguimientosListView,
    SeguimientoCreateView,
    SeguimientoUpdateView,
    SeguimientoDeleteView,
    ProveedoresListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDeleteView,
    TiposGastoListView,
    TipoGastoCreateView,
    TipoGastoUpdateView,
    TipoGastoDeleteView,
    ComprasListView,
    CompraCreateView,
    CompraUpdateView,
    CompraDeleteView,
    GastosListView,
    GastoCreateView,
    GastoUpdateView,
    GastoDeleteView,
    PlanesListView,
    PlanCreateView,
    PlanUpdateView,
    PlanDeleteView,
    ObjetivosListView,
    ObjetivoCreateView,
    ObjetivoUpdateView,
    ObjetivoDeleteView,
    ActividadesListView,
    ActividadCreateView,
    ActividadUpdateView,
    ActividadDeleteView,
    HistorialesListView,
    HistorialCreateView,
    HistorialUpdateView,
    HistorialDeleteView,
    EvolucionesListView,
    EvolucionCreateView,
    EvolucionUpdateView,
    EvolucionDeleteView,
    RegistrosListView,
    RegistroCreateView,
    RegistroUpdateView,
    RegistroDeleteView,
    NotasListView,
    NotaCreateView,
    NotaUpdateView,
    NotaDeleteView,
    UsuariosListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioDeleteView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RedirectView.as_view(url='/login/', permanent=False), name='register'),
    
    # Pacientes CRUD
    path('pacientes/', PacientesListView.as_view(), name='pacientes_list'),
    path('pacientes/crear/', PacienteCreateView.as_view(), name='paciente_create'),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name='paciente_detail'),
    path('pacientes/<int:pk>/legajo/imprimir/', PacienteLegajoPrintView.as_view(), name='paciente_legajo_print'),
    path('pacientes/editar/<int:pk>/', PacienteUpdateView.as_view(), name='paciente_update'),
    path('pacientes/eliminar/<int:pk>/', PacienteDeleteView.as_view(), name='paciente_delete'),
    
    # Empleados CRUD
    path('empleados/', EmpleadosListView.as_view(), name='empleados_list'),
    path('empleados/crear/', EmpleadoCreateView.as_view(), name='empleado_create'),
    path('empleados/editar/<int:pk>/', EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('empleados/eliminar/<int:pk>/', EmpleadoDeleteView.as_view(), name='empleado_delete'),
    
    # Salas CRUD
    path('salas/', SalasListView.as_view(), name='salas_list'),
    path('salas/crear/', SalaCreateView.as_view(), name='sala_create'),
    path('salas/editar/<int:pk>/', SalaUpdateView.as_view(), name='sala_update'),
    path('salas/eliminar/<int:pk>/', SalaDeleteView.as_view(), name='sala_delete'),
    
    # Áreas CRUD
    path('areas/', AreasListView.as_view(), name='areas_list'),
    path('areas/crear/', AreaCreateView.as_view(), name='area_create'),
    path('areas/editar/<int:pk>/', AreaUpdateView.as_view(), name='area_update'),
    path('areas/eliminar/<int:pk>/', AreaDeleteView.as_view(), name='area_delete'),
    
    # Diagnósticos CRUD
    path('diagnosticos/', DiagnosticosListView.as_view(), name='diagnosticos_list'),
    path('diagnosticos/crear/', DiagnosticoCreateView.as_view(), name='diagnostico_create'),
    path('diagnosticos/editar/<int:pk>/', DiagnosticoUpdateView.as_view(), name='diagnostico_update'),
    path('diagnosticos/eliminar/<int:pk>/', DiagnosticoDeleteView.as_view(), name='diagnostico_delete'),
    
    # Seguimientos CRUD
    path('seguimientos/', SeguimientosListView.as_view(), name='seguimientos_list'),
    path('seguimientos/crear/', SeguimientoCreateView.as_view(), name='seguimiento_create'),
    path('seguimientos/editar/<int:pk>/', SeguimientoUpdateView.as_view(), name='seguimiento_update'),
    path('seguimientos/eliminar/<int:pk>/', SeguimientoDeleteView.as_view(), name='seguimiento_delete'),
    
    # Documentos CRUD
    path('documentos/', DocumentosListView.as_view(), name='documentos_list'),
    path('documentos/crear/', DocumentoCreateView.as_view(), name='documento_create'),
    path('documentos/editar/<int:pk>/', DocumentoUpdateView.as_view(), name='documento_update'),
    path('documentos/eliminar/<int:pk>/', DocumentoDeleteView.as_view(), name='documento_delete'),
    
    # Proveedores CRUD
    path('proveedores/', ProveedoresListView.as_view(), name='proveedores_list'),
    path('proveedores/crear/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/editar/<int:pk>/', ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/eliminar/<int:pk>/', ProveedorDeleteView.as_view(), name='proveedor_delete'),
    
    # Tipos de Gasto CRUD
    path('tipos-gasto/', TiposGastoListView.as_view(), name='tipos_gasto_list'),
    path('tipos-gasto/crear/', TipoGastoCreateView.as_view(), name='tipo_gasto_create'),
    path('tipos-gasto/editar/<int:pk>/', TipoGastoUpdateView.as_view(), name='tipo_gasto_update'),
    path('tipos-gasto/eliminar/<int:pk>/', TipoGastoDeleteView.as_view(), name='tipo_gasto_delete'),
    
    # Compras CRUD
    path('compras/', ComprasListView.as_view(), name='compras_list'),
    path('compras/crear/', CompraCreateView.as_view(), name='compra_create'),
    path('compras/editar/<int:pk>/', CompraUpdateView.as_view(), name='compra_update'),
    path('compras/eliminar/<int:pk>/', CompraDeleteView.as_view(), name='compra_delete'),
    
    # Gastos CRUD
    path('gastos/', GastosListView.as_view(), name='gastos_list'),
    path('gastos/crear/', GastoCreateView.as_view(), name='gasto_create'),
    path('gastos/editar/<int:pk>/', GastoUpdateView.as_view(), name='gasto_update'),
    path('gastos/eliminar/<int:pk>/', GastoDeleteView.as_view(), name='gasto_delete'),
    
    # Listados (requieren login)
    path('turnos/', TurnosListView.as_view(), name='turnos_list'),
    path('tratamientos/', TratamientosListView.as_view(), name='tratamientos_list'),
    path('servicios/', ServiciosListView.as_view(), name='servicios_list'),
    path('facturacion/', FacturacionListView.as_view(), name='facturacion_list'),
    path('inventario/', InventarioListView.as_view(), name='inventario_list'),
    
    # Planes de Tratamiento CRUD
    path('planes/', PlanesListView.as_view(), name='planes_list'),
    path('planes/crear/', PlanCreateView.as_view(), name='plan_create'),
    path('planes/editar/<int:pk>/', PlanUpdateView.as_view(), name='plan_update'),
    path('planes/eliminar/<int:pk>/', PlanDeleteView.as_view(), name='plan_delete'),
    
    # Objetivos de Tratamiento CRUD
    path('objetivos/', ObjetivosListView.as_view(), name='objetivos_list'),
    path('objetivos/crear/', ObjetivoCreateView.as_view(), name='objetivo_create'),
    path('objetivos/editar/<int:pk>/', ObjetivoUpdateView.as_view(), name='objetivo_update'),
    path('objetivos/eliminar/<int:pk>/', ObjetivoDeleteView.as_view(), name='objetivo_delete'),
    
    # Actividades de Plan CRUD
    path('actividades/', ActividadesListView.as_view(), name='actividades_list'),
    path('actividades/crear/', ActividadCreateView.as_view(), name='actividad_create'),
    path('actividades/editar/<int:pk>/', ActividadUpdateView.as_view(), name='actividad_update'),
    path('actividades/eliminar/<int:pk>/', ActividadDeleteView.as_view(), name='actividad_delete'),
    
    # Historiales Médicos CRUD
    path('historiales/', HistorialesListView.as_view(), name='historiales_list'),
    path('historiales/crear/', HistorialCreateView.as_view(), name='historial_create'),
    path('historiales/editar/<int:pk>/', HistorialUpdateView.as_view(), name='historial_update'),
    path('historiales/eliminar/<int:pk>/', HistorialDeleteView.as_view(), name='historial_delete'),
    
    # Evoluciones Semanales CRUD
    path('evoluciones/', EvolucionesListView.as_view(), name='evoluciones_list'),
    path('evoluciones/crear/', EvolucionCreateView.as_view(), name='evolucion_create'),
    path('evoluciones/editar/<int:pk>/', EvolucionUpdateView.as_view(), name='evolucion_update'),
    path('evoluciones/eliminar/<int:pk>/', EvolucionDeleteView.as_view(), name='evolucion_delete'),
    
    # Registros de Actividad CRUD
    path('registros/', RegistrosListView.as_view(), name='registros_list'),
    path('registros/crear/', RegistroCreateView.as_view(), name='registro_create'),
    path('registros/editar/<int:pk>/', RegistroUpdateView.as_view(), name='registro_update'),
    path('registros/eliminar/<int:pk>/', RegistroDeleteView.as_view(), name='registro_delete'),
    
    # Notas Importantes CRUD
    path('notas/', NotasListView.as_view(), name='notas_list'),
    path('notas/crear/', NotaCreateView.as_view(), name='nota_create'),
    path('notas/editar/<int:pk>/', NotaUpdateView.as_view(), name='nota_update'),
    path('notas/eliminar/<int:pk>/', NotaDeleteView.as_view(), name='nota_delete'),

    # Usuarios CRUD (solo admin)
    path('usuarios/', UsuariosListView.as_view(), name='usuarios_list'),
    path('usuarios/crear/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/editar/<int:pk>/', UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/eliminar/<int:pk>/', UsuarioDeleteView.as_view(), name='usuario_delete'),
]