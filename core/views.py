from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy

from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Contar estadísticas para el dashboard
            from pacientes.models import Paciente
            from turnos.models import Turno, EstadoTurno
            from tratamientos.models import PlanTratamiento
            from empleados.models import Empleado
            from django.utils import timezone
            
            context['pacientes_count'] = Paciente.objects.filter(activo=True).count()
            context['turnos_hoy_count'] = Turno.objects.filter(
                fecha=timezone.now().date()
            ).exclude(estado=EstadoTurno.CANCELADO).count()
            context['tratamientos_count'] = PlanTratamiento.objects.filter(activo=True).count()
            context['empleados_count'] = Empleado.objects.filter(activo=True).count()
        return context


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class RegisterView(TemplateView):
    template_name = 'registration/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomUserCreationForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asignar al grupo Paciente por defecto
            from django.contrib.auth.models import Group
            paciente_group, _ = Group.objects.get_or_create(name='Paciente')
            user.groups.add(paciente_group)
            
            # Crear Persona asociada si no existe
            from personas.models import Persona
            Persona.objects.get_or_create(
                dni=user.dni,
                defaults={
                    'nombre': user.first_name,
                    'apellido': user.last_name,
                    'activo': True,
                }
            )
            
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente! Bienvenido a Centro de Día Proyectar.')
            return redirect('home')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


# Vistas de listado (solo lectura, con permisos)
class PacientesListView(LoginRequiredMixin, TemplateView):
    template_name = 'pacientes/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from pacientes.models import Paciente
        context['pacientes'] = Paciente.objects.select_related('persona', 'obra_social').filter(activo=True).order_by('-fecha_ingreso')
        return context


class TurnosListView(LoginRequiredMixin, TemplateView):
    template_name = 'turnos/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from turnos.models import Turno, EstadoTurno
        from django.utils import timezone
        context['turnos'] = Turno.objects.select_related(
            'paciente__persona', 'profesional__persona', 'servicio'
        ).exclude(estado=EstadoTurno.CANCELADO).order_by('fecha', 'hora_inicio')
        context['hoy'] = timezone.now().date()
        return context


class TratamientosListView(LoginRequiredMixin, TemplateView):
    template_name = 'tratamientos/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tratamientos.models import PlanTratamiento
        context['tratamientos'] = PlanTratamiento.objects.select_related('paciente__persona').filter(activo=True).order_by('-fecha_inicio')
        return context


class EmpleadosListView(LoginRequiredMixin, TemplateView):
    template_name = 'empleados/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from empleados.models import Empleado
        context['empleados'] = Empleado.objects.select_related('persona').filter(activo=True).order_by('persona__apellido')
        return context


class ServiciosListView(LoginRequiredMixin, TemplateView):
    template_name = 'servicios/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from servicios.models import Servicio
        context['servicios'] = Servicio.objects.select_related('tipo_servicio').filter(activo=True).order_by('tipo_servicio__nombre', 'nombre')
        return context


class FacturacionListView(LoginRequiredMixin, TemplateView):
    template_name = 'facturacion/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from facturacion.models import FacturaVenta, EstadoFactura
        context['facturas'] = FacturaVenta.objects.select_related('paciente__persona', 'obra_social').exclude(estado=EstadoFactura.ANULADA).order_by('-fecha')
        return context


class InventarioListView(LoginRequiredMixin, TemplateView):
    template_name = 'inventario/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from inventario.models import Producto
        context['productos'] = Producto.objects.select_related('categoria').filter(activo=True).order_by('nombre')
        return context


class ComprasListView(LoginRequiredMixin, TemplateView):
    template_name = 'compras/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from compras.models import Compra
        context['compras'] = Compra.objects.select_related('proveedor').filter(activo=True).order_by('-fecha')
        return context


class DocumentosListView(LoginRequiredMixin, TemplateView):
    template_name = 'documentos/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from documentos.models import Documento
        context['documentos'] = Documento.objects.select_related('persona').filter(activo=True).order_by('-fecha_creacion')
        return context