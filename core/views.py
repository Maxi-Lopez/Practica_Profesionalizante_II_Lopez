from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy

from usuarios.models import Usuario
from usuarios.forms import CustomUserCreationForm
from core.forms import PacienteForm, EmpleadoForm, SalaForm, AreaInterdisciplinariaForm, DiagnosticoAreaForm, SeguimientoTrimestralForm
from pacientes.models import Sala, AreaInterdisciplinaria, DiagnosticoArea, SeguimientoTrimestral


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


class PacienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None  # Usamos form_class en lugar de model
    form_class = PacienteForm
    template_name = 'pacientes/form.html'
    success_url = reverse_lazy('pacientes_list')
    login_url = 'login'
    permission_required = 'pacientes.add_paciente'
    
    def get_permission_required(self):
        # Permitir a admin, profesional y recepcionista
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.add_paciente',)
    
    def form_valid(self, form):
        messages.success(self.request, 'Paciente creado exitosamente.')
        return super().form_valid(form)


class PacienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None  # Usamos form_class en lugar de model
    form_class = PacienteForm
    template_name = 'pacientes/form.html'
    success_url = reverse_lazy('pacientes_list')
    login_url = 'login'
    permission_required = 'pacientes.change_paciente'
    pk_url_kwarg = 'pk'
    
    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.change_paciente',)
    
    def get_object(self, queryset=None):
        from pacientes.models import Paciente
        return Paciente.objects.select_related('persona').get(pk=self.kwargs['pk'])
    
    def form_valid(self, form):
        messages.success(self.request, 'Paciente actualizado exitosamente.')
        return super().form_valid(form)


class PacienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'pacientes/confirm_delete.html'
    success_url = reverse_lazy('pacientes_list')
    login_url = 'login'
    permission_required = 'pacientes.delete_paciente'
    pk_url_kwarg = 'pk'
    
    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.delete_paciente',)
    
    def get_object(self, queryset=None):
        from pacientes.models import Paciente
        return Paciente.objects.select_related('persona').get(pk=self.kwargs['pk'])
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Paciente dado de baja exitosamente.')
        return super().delete(request, *args, **kwargs)


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
        context['compras'] = Compra.objects.select_related('proveedor').filter(anulada=False).order_by('-fecha')
        return context


class DocumentosListView(LoginRequiredMixin, TemplateView):
    template_name = 'documentos/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from documentos.models import Documento
        context['documentos'] = Documento.objects.select_related('persona').filter(activo=True).order_by('-fecha_creacion')
        return context


# ============================================================
# EMPLEADOS CRUD (HTML)
# ============================================================

class EmpleadoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = EmpleadoForm
    template_name = 'empleados/form.html'
    success_url = reverse_lazy('empleados_list')
    login_url = 'login'
    permission_required = 'empleados.add_empleado'
    
    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('empleados.add_empleado',)
    
    def form_valid(self, form):
        messages.success(self.request, 'Empleado creado exitosamente.')
        return super().form_valid(form)


class EmpleadoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = EmpleadoForm
    template_name = 'empleados/form.html'
    success_url = reverse_lazy('empleados_list')
    login_url = 'login'
    permission_required = 'empleados.change_empleado'
    pk_url_kwarg = 'pk'
    
    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('empleados.change_empleado',)
    
    def get_object(self, queryset=None):
        from empleados.models import Empleado
        return Empleado.objects.select_related('persona').get(pk=self.kwargs['pk'])
    
    def form_valid(self, form):
        messages.success(self.request, 'Empleado actualizado exitosamente.')
        return super().form_valid(form)


class EmpleadoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'empleados/confirm_delete.html'
    success_url = reverse_lazy('empleados_list')
    login_url = 'login'
    permission_required = 'empleados.delete_empleado'
    pk_url_kwarg = 'pk'
    
    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('empleados.delete_empleado',)
    
    def get_object(self, queryset=None):
        from empleados.models import Empleado
        return Empleado.objects.select_related('persona').get(pk=self.kwargs['pk'])
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Empleado dado de baja exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================
# SALAS CRUD (HTML)
# ============================================================

class SalasListView(LoginRequiredMixin, ListView):
    model = Sala
    template_name = 'salas/list.html'
    context_object_name = 'salas'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return Sala.objects.filter(activo=True).select_related('orientador__persona').order_by('nombre')


class SalaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = SalaForm
    template_name = 'salas/form.html'
    success_url = reverse_lazy('salas_list')
    login_url = 'login'
    permission_required = 'pacientes.add_sala'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.add_sala',)

    def form_valid(self, form):
        messages.success(self.request, 'Sala creada exitosamente.')
        return super().form_valid(form)


class SalaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = SalaForm
    template_name = 'salas/form.html'
    success_url = reverse_lazy('salas_list')
    login_url = 'login'
    permission_required = 'pacientes.change_sala'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.change_sala',)

    def get_object(self, queryset=None):
        return Sala.objects.select_related('orientador__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Sala actualizada exitosamente.')
        return super().form_valid(form)


class SalaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'salas/confirm_delete.html'
    success_url = reverse_lazy('salas_list')
    login_url = 'login'
    permission_required = 'pacientes.delete_sala'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.delete_sala',)

    def get_object(self, queryset=None):
        return Sala.objects.select_related('orientador__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Sala dada de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# ÁREAS INTERDISCIPLINARIAS CRUD (HTML)
# ============================================================

class AreasListView(LoginRequiredMixin, ListView):
    model = AreaInterdisciplinaria
    template_name = 'areas/list.html'
    context_object_name = 'areas'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return AreaInterdisciplinaria.objects.filter(activo=True).order_by('nombre')


class AreaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = AreaInterdisciplinariaForm
    template_name = 'areas/form.html'
    success_url = reverse_lazy('areas_list')
    login_url = 'login'
    permission_required = 'pacientes.add_areainterdisciplinaria'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.add_areainterdisciplinaria',)

    def form_valid(self, form):
        messages.success(self.request, 'Área creada exitosamente.')
        return super().form_valid(form)


class AreaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = AreaInterdisciplinariaForm
    template_name = 'areas/form.html'
    success_url = reverse_lazy('areas_list')
    login_url = 'login'
    permission_required = 'pacientes.change_areainterdisciplinaria'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.change_areainterdisciplinaria',)

    def get_object(self, queryset=None):
        return AreaInterdisciplinaria.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Área actualizada exitosamente.')
        return super().form_valid(form)


class AreaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'areas/confirm_delete.html'
    success_url = reverse_lazy('areas_list')
    login_url = 'login'
    permission_required = 'pacientes.delete_areainterdisciplinaria'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.delete_areainterdisciplinaria',)

    def get_object(self, queryset=None):
        return AreaInterdisciplinaria.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Área dada de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# DIAGNÓSTICOS POR ÁREA CRUD (HTML)
# ============================================================

class DiagnosticosListView(LoginRequiredMixin, ListView):
    model = DiagnosticoArea
    template_name = 'diagnosticos/list.html'
    context_object_name = 'diagnosticos'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return DiagnosticoArea.objects.filter(activo=True).select_related(
            'paciente__persona', 'area', 'profesional__persona'
        ).order_by('-fecha')


class DiagnosticoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = DiagnosticoAreaForm
    template_name = 'diagnosticos/form.html'
    success_url = reverse_lazy('diagnosticos_list')
    login_url = 'login'
    permission_required = 'pacientes.add_diagnosticoarea'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.add_diagnosticoarea',)

    def form_valid(self, form):
        messages.success(self.request, 'Diagnóstico creado exitosamente.')
        return super().form_valid(form)


class DiagnosticoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = DiagnosticoAreaForm
    template_name = 'diagnosticos/form.html'
    success_url = reverse_lazy('diagnosticos_list')
    login_url = 'login'
    permission_required = 'pacientes.change_diagnosticoarea'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.change_diagnosticoarea',)

    def get_object(self, queryset=None):
        return DiagnosticoArea.objects.select_related(
            'paciente__persona', 'area', 'profesional__persona'
        ).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Diagnóstico actualizado exitosamente.')
        return super().form_valid(form)


class DiagnosticoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'diagnosticos/confirm_delete.html'
    success_url = reverse_lazy('diagnosticos_list')
    login_url = 'login'
    permission_required = 'pacientes.delete_diagnosticoarea'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.delete_diagnosticoarea',)

    def get_object(self, queryset=None):
        return DiagnosticoArea.objects.select_related(
            'paciente__persona', 'area', 'profesional__persona'
        ).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Diagnóstico dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# SEGUIMIENTOS TRIMESTRALES CRUD (HTML)
# ============================================================

class SeguimientosListView(LoginRequiredMixin, ListView):
    model = SeguimientoTrimestral
    template_name = 'seguimientos/list.html'
    context_object_name = 'seguimientos'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return SeguimientoTrimestral.objects.filter(activo=True).select_related(
            'paciente__persona', 'area', 'profesional__persona'
        ).order_by('-fecha')


class SeguimientoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = SeguimientoTrimestralForm
    template_name = 'seguimientos/form.html'
    success_url = reverse_lazy('seguimientos_list')
    login_url = 'login'
    permission_required = 'pacientes.add_seguimientotrimestral'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.add_seguimientotrimestral',)

    def form_valid(self, form):
        messages.success(self.request, 'Seguimiento creado exitosamente.')
        return super().form_valid(form)


class SeguimientoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = SeguimientoTrimestralForm
    template_name = 'seguimientos/form.html'
    success_url = reverse_lazy('seguimientos_list')
    login_url = 'login'
    permission_required = 'pacientes.change_seguimientotrimestral'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.change_seguimientotrimestral',)

    def get_object(self, queryset=None):
        return SeguimientoTrimestral.objects.select_related(
            'paciente__persona', 'area', 'profesional__persona'
        ).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Seguimiento actualizado exitosamente.')
        return super().form_valid(form)


class SeguimientoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'seguimientos/confirm_delete.html'
    success_url = reverse_lazy('seguimientos_list')
    login_url = 'login'
    permission_required = 'pacientes.delete_seguimientotrimestral'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('pacientes.delete_seguimientotrimestral',)

    def get_object(self, queryset=None):
        return SeguimientoTrimestral.objects.select_related(
            'paciente__persona', 'area', 'profesional__persona'
        ).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Seguimiento dado de baja exitosamente.')
        return redirect(self.success_url)