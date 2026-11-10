from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
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
from documentos.routers import router as documentos_router

urlpatterns = [
    path("admin/", admin.site.urls),

    # Web Interface (HTML templates)
    path("", include("core.urls")),

    # Password Reset (Django built-in views)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done'),
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete'),
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),

    # API REST
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
    path("api/documentos/", include(documentos_router.urls)),

    # Documentación API (Swagger/OpenAPI)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)