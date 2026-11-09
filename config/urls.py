from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from personas.routers import router as personas_router
from pacientes.routers import router as pacientes_router
from empleados.routers import router as empleados_router

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("usuarios.urls")),
    path("api/personas/", include(personas_router.urls)),
    path("api/pacientes/", include(pacientes_router.urls)),
    path("api/empleados/", include(empleados_router.urls)),

    # Documentación API (Swagger/OpenAPI)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]