from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from personas.routers import router as personas_router
from pacientes.routers import router as pacientes_router
from empleados.routers import router as empleados_router
from servicios.routers import router as servicios_router
from turnos.routers import router as turnos_router
from tratamientos.routers import router as tratamientos_router
from facturacion.routers import router as facturacion_router
from inventario.routers import router as inventario_router
from compras.routers import router as compras_router

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("usuarios.urls")),
    path("api/personas/", include(personas_router.urls)),
    path("api/pacientes/", include(pacientes_router.urls)),
    path("api/empleados/", include(empleados_router.urls)),
    path("api/servicios/", include(servicios_router.urls)),
    path("api/turnos/", include(turnos_router.urls)),
    path("api/tratamientos/", include(tratamientos_router.urls)),
    path("api/facturacion/", include(facturacion_router.urls)),
    path("api/inventario/", include(inventario_router.urls)),
    path("api/compras/", include(compras_router.urls)),

    # Documentación API (Swagger/OpenAPI)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]