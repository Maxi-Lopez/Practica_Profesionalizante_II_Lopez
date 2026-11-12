from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import models
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from usuarios.models import Usuario
from usuarios.forms import UsuarioAdminForm
from core.forms import TurnoForm
from core.forms import PacienteForm, EmpleadoForm, DocumentoForm, SalaForm, AreaInterdisciplinariaForm, DiagnosticoAreaForm, SeguimientoTrimestralForm, ProveedorForm, TipoGastoForm, CompraForm, GastoForm, PlanTratamientoForm, ObjetivoTratamientoForm, ActividadPlanForm, HistorialMedicoForm, EvolucionSemanalForm, RegistroActividadForm, NotaImportanteForm
from pacientes.models import Sala, AreaInterdisciplinaria, DiagnosticoArea, SeguimientoTrimestral, Paciente
from turnos.models import Turno, EstadoTurno
from compras.models import Proveedor, Compra, TipoGasto, Gasto
from tratamientos.models import PlanTratamiento, ObjetivoTratamiento, ActividadPlan, HistorialMedico, EvolucionSemanal, RegistroActividad, NotaImportante


def health_check(request):
    """Health check endpoint para Render/Load Balancers."""
    return JsonResponse({'status': 'ok', 'service': 'centro-salud-api'})


class SoloAdminMixin:
    """Restringe el acceso a admin/superuser."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not (request.user.is_superuser or getattr(request.user, 'rol', None) == 'admin'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


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
            from django.db import models
            
            user = self.request.user
            hoy = timezone.now().date()
            
            if user.is_superuser or user.rol in ['admin', 'orientador']:
                # Admin y orientador ven todo
                context['pacientes_count'] = Paciente.objects.filter(activo=True).count()
                context['turnos_hoy_count'] = Turno.objects.filter(
                    fecha=hoy
                ).exclude(estado=EstadoTurno.CANCELADO).count()
                context['tratamientos_count'] = PlanTratamiento.objects.filter(activo=True).count()
                context['empleados_count'] = Empleado.objects.filter(activo=True).count()
                context['es_admin'] = True
            elif user.rol in ['recepcionista']:
                # Recepcionista ve todo (gestión de turnos y pacientes)
                context['pacientes_count'] = Paciente.objects.filter(activo=True).count()
                context['turnos_hoy_count'] = Turno.objects.filter(
                    fecha=hoy
                ).exclude(estado=EstadoTurno.CANCELADO).count()
                context['tratamientos_count'] = PlanTratamiento.objects.filter(activo=True).count()
                context['empleados_count'] = Empleado.objects.filter(activo=True).count()
                context['es_admin'] = False
            elif user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
                # Profesionales ven solo sus pacientes/turnos/tratamientos
                if user.area:
                    pacientes_qs = Paciente.objects.filter(activo=True).filter(
                        models.Q(diagnosticos_area__activo=True, diagnosticos_area__area=user.area) |
                        models.Q(seguimientos_trimestrales__activo=True, seguimientos_trimestrales__area=user.area)
                    ).distinct()
                    
                    context['pacientes_count'] = pacientes_qs.count()
                    context['turnos_hoy_count'] = Turno.objects.filter(
                        fecha=hoy,
                        paciente__in=pacientes_qs
                    ).exclude(estado=EstadoTurno.CANCELADO).count()
                    context['tratamientos_count'] = PlanTratamiento.objects.filter(
                        activo=True, paciente__in=pacientes_qs
                    ).count()
                    context['empleados_count'] = 0  # No relevante para profesionales
                else:
                    context['pacientes_count'] = 0
                    context['turnos_hoy_count'] = 0
                    context['tratamientos_count'] = 0
                    context['empleados_count'] = 0
                context['es_admin'] = False
                context['es_profesional'] = True
            else:
                context['pacientes_count'] = 0
                context['turnos_hoy_count'] = 0
                context['tratamientos_count'] = 0
                context['empleados_count'] = 0
                context['es_admin'] = False
        return context


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


# ============================================================
# PACIENTE DETAIL & LEGAJO PRINT
# ============================================================

class PacienteDetailView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'pacientes/detail.html'
    context_object_name = 'paciente'
    login_url = 'login'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # Allow: superuser, admin, orientador, recepcionista, profesionales
        user = request.user
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            return super().dispatch(request, *args, **kwargs)
        # Profesionales can view patients in their area
        if user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            # Check if patient has any diagnostico/seguimiento/turno in user's area
            paciente = self.get_object()
            if self.paciente_en_area_del_profesional(paciente, user):
                return super().dispatch(request, *args, **kwargs)
            raise PermissionDenied("No tiene permiso para ver este paciente.")
        raise PermissionDenied("No tiene permiso para ver pacientes.")

    def paciente_en_area_del_profesional(self, paciente, user):
        """Verifica si el paciente tiene relación con el área del profesional."""
        if not user.area:
            return False
        # Verificar diagnósticos en el área
        if paciente.diagnosticos_area.filter(activo=True, area=user.area).exists():
            return True
        # Verificar seguimientos en el área
        if paciente.seguimientos_trimestrales.filter(activo=True, area=user.area).exists():
            return True
        # Verificar turnos con profesional del área (a través de Empleado)
        # Nota: No hay link directo Usuario-Empleado, así que usamos área
        return False

    def get_queryset(self):
        user = self.request.user
        base_qs = Paciente.objects.filter(activo=True).select_related(
            'persona', 'obra_social', 'sala', 'sala__orientador__persona'
        )
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            return base_qs
        if user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            if user.area:
                # Filtrar pacientes que tienen diagnosticos/seguimientos en el área del profesional
                return base_qs.filter(
                    models.Q(diagnosticos_area__activo=True, diagnosticos_area__area=user.area) |
                    models.Q(seguimientos_trimestrales__activo=True, seguimientos_trimestrales__area=user.area)
                ).distinct()
            return Paciente.objects.none()
        return Paciente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['perms'] = self.request.user.get_all_permissions()
        
        paciente = self.object
        hoy = timezone.now().date()
        
        # Flags para CUD
        if paciente.fecha_vencimiento_cud:
            context['cud_vencido'] = paciente.fecha_vencimiento_cud <= hoy
            context['cud_proximo_a_vencer'] = (
                not context['cud_vencido'] and 
                paciente.fecha_vencimiento_cud <= hoy + timedelta(days=30)
            )
        else:
            context['cud_vencido'] = False
            context['cud_proximo_a_vencer'] = False
        
        # Flags para Pases de Transporte
        if paciente.pases_transporte_vencimiento:
            context['pases_vencidos'] = paciente.pases_transporte_vencimiento <= hoy
            context['pases_proximos_a_vencer'] = (
                not context['pases_vencidos'] and 
                paciente.pases_transporte_vencimiento <= hoy + timedelta(days=30)
            )
        else:
            context['pases_vencidos'] = False
            context['pases_proximos_a_vencer'] = False
        
        return context


class PacienteLegajoPrintView(LoginRequiredMixin, DetailView):
    model = Paciente
    template_name = 'pacientes/legajo_print.html'
    context_object_name = 'paciente'
    login_url = 'login'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        user = request.user
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            return super().dispatch(request, *args, **kwargs)
        if user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            paciente = self.get_object()
            if self.paciente_en_area_del_profesional(paciente, user):
                return super().dispatch(request, *args, **kwargs)
            raise PermissionDenied("No tiene permiso para imprimir el legajo de este paciente.")
        raise PermissionDenied("No tiene permiso para imprimir legajos.")

    def paciente_en_area_del_profesional(self, paciente, user):
        if not user.area:
            return False
        if paciente.diagnosticos_area.filter(activo=True, area=user.area).exists():
            return True
        if paciente.seguimientos_trimestrales.filter(activo=True, area=user.area).exists():
            return True
        return False

    def get_queryset(self):
        user = self.request.user
        base_qs = Paciente.objects.filter(activo=True).select_related(
            'persona', 'obra_social', 'sala', 'sala__orientador__persona'
        ).prefetch_related(
            'persona__telefonos',
            'persona__emails',
            'diagnosticos_area__area',
            'diagnosticos_area__profesional__persona',
            'seguimientos_trimestrales__area',
            'seguimientos_trimestrales__profesional__persona',
            'persona__documentos'
        )
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            return base_qs
        if user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            if user.area:
                return base_qs.filter(
                    models.Q(diagnosticos_area__activo=True, diagnosticos_area__area=user.area) |
                    models.Q(seguimientos_trimestrales__activo=True, seguimientos_trimestrales__area=user.area)
                ).distinct()
            return Paciente.objects.none()
        return Paciente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.object
        context['telefonos'] = paciente.persona.telefonos.filter(activo=True)
        context['emails'] = paciente.persona.emails.filter(activo=True)
        context['diagnosticos'] = paciente.diagnosticos_area.filter(activo=True).select_related(
            'area', 'profesional__persona'
        ).order_by('-fecha')
        context['seguimientos'] = paciente.seguimientos_trimestrales.filter(activo=True).select_related(
            'area', 'profesional__persona'
        ).order_by('-fecha')
        context['documentos'] = paciente.persona.documentos.filter(activo=True).order_by('-fecha_documento')
        context['fecha_impresion'] = timezone.now()
        context['usuario_impresion'] = self.request.user.get_full_name() or self.request.user.username
        
        # Flags para CUD
        hoy = timezone.now().date()
        if paciente.fecha_vencimiento_cud:
            context['cud_vencido'] = paciente.fecha_vencimiento_cud <= hoy
            context['cud_proximo_a_vencer'] = (
                not context['cud_vencido'] and 
                paciente.fecha_vencimiento_cud <= hoy + timedelta(days=30)
            )
        else:
            context['cud_vencido'] = False
            context['cud_proximo_a_vencer'] = False
        
        # Flags para Pases de Transporte
        if paciente.pases_transporte_vencimiento:
            context['pases_vencidos'] = paciente.pases_transporte_vencimiento <= hoy
            context['pases_proximos_a_vencer'] = (
                not context['pases_vencidos'] and 
                paciente.pases_transporte_vencimiento <= hoy + timedelta(days=30)
            )
        else:
            context['pases_vencidos'] = False
            context['pases_proximos_a_vencer'] = False
        
        return context


# Vistas de listado (solo lectura, con permisos)
class PacientesListView(LoginRequiredMixin, TemplateView):
    template_name = 'pacientes/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from pacientes.models import Paciente
        from personas.models import Email
        from django.db.models import Q
        user = self.request.user
        
        base_qs = Paciente.objects.select_related('persona', 'obra_social').filter(activo=True).order_by('-fecha_ingreso')
        
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            context['pacientes'] = base_qs
        elif user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            # Profesional: ver pacientes que tienen turnos asignados A ÉL, 
            # O diagnosticos/seguimientos en SU ÁREA
            profesional_qs = Paciente.objects.none()
            if user.email:
                # Buscar empleados vinculados por email
                empleado_personas = Email.objects.filter(
                    direccion_email=user.email, activo=True
                ).values_list('persona_id', flat=True)
                if empleado_personas:
                    profesional_qs = base_qs.filter(
                        turnos__profesional__persona_id__in=empleado_personas
                    ).distinct()
            
            # También incluir pacientes de su área (diagnósticos/seguimientos)
            area_qs = Paciente.objects.none()
            if user.area:
                area_qs = base_qs.filter(
                    Q(diagnosticos_area__activo=True, diagnosticos_area__area=user.area) |
                    Q(seguimientos_trimestrales__activo=True, seguimientos_trimestrales__area=user.area)
                ).distinct()
            
            # Unir ambos querysets
            if profesional_qs and area_qs:
                context['pacientes'] = (profesional_qs | area_qs).distinct()
            elif profesional_qs:
                context['pacientes'] = profesional_qs
            elif area_qs:
                context['pacientes'] = area_qs
            else:
                context['pacientes'] = Paciente.objects.none()
        else:
            context['pacientes'] = Paciente.objects.none()
        
        # Aplicar búsqueda si existe el parámetro
        search = self.request.GET.get('search', '').strip()
        if search:
            search_q = Q(persona__nombre__icontains=search) | \
                       Q(persona__apellido__icontains=search) | \
                       Q(persona__dni__icontains=search) | \
                       Q(obra_social__nombre__icontains=search)
            context['pacientes'] = context['pacientes'].filter(search_q)
        
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
        from servicios.models import Servicio
        from pacientes.models import Paciente
        from empleados.models import Empleado
        from django.utils import timezone
        from django.db.models import Q
        import logging
        logger = logging.getLogger(__name__)
        user = self.request.user
        
        base_qs = Turno.objects.select_related(
            'paciente__persona', 'profesional__persona', 'servicio'
        ).exclude(estado=EstadoTurno.CANCELADO).order_by('fecha', 'hora_inicio')
        
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            context['turnos'] = base_qs
        elif user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            # Profesional: ver solo SUS turnos (vinculado directo Empleado.usuario)
            prof = self._get_profesional_for_user(user)
            if prof:
                context['turnos'] = base_qs.filter(profesional=prof)
            else:
                logger.warning(f"No se encontró Empleado para usuario {user.username} (rol: {user.rol})")
                context['turnos'] = Turno.objects.none()
        else:
            context['turnos'] = Turno.objects.none()
        
        # Aplicar búsqueda si existe el parámetro
        search = self.request.GET.get('search', '').strip()
        if search:
            search_q = Q(paciente__persona__nombre__icontains=search) | \
                       Q(paciente__persona__apellido__icontains=search) | \
                       Q(paciente__persona__dni__icontains=search) | \
                       Q(profesional__persona__nombre__icontains=search) | \
                       Q(profesional__persona__apellido__icontains=search) | \
                       Q(servicio__nombre__icontains=search)
            context['turnos'] = context['turnos'].filter(search_q)
        
        # Para el modal: pacientes y servicios
        context['pacientes'] = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        context['servicios'] = Servicio.objects.filter(activo=True).order_by('nombre')
        
        # Profesionales para el dropdown (admin/recepcionista/orientador)
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            context['profesionales'] = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
            # Serializar para Alpine.js
            import json
            context['profesionales_json'] = json.dumps([
                {'id': p.id, 'nombre': f'{p.persona.apellido}, {p.persona.nombre} (DNI: {p.persona.dni})'} 
                for p in context['profesionales']
            ])
        else:
            context['profesionales'] = Empleado.objects.none()
            context['profesionales_json'] = '[]'
        
        # ID del profesional actual (para profesionales)
        if user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            prof = self._get_profesional_for_user(user)
            if prof:
                context['profesional_id'] = prof.id
            else:
                logger.warning(f"No se encontró Empleado para usuario {user.username} (email: {user.email}, rol: {user.rol})")
        
        context['hoy'] = timezone.now().date()
        
        # Generar slots de hora (00:00 a 23:30 en intervalos de 30 min)
        time_slots = []
        for h in range(24):
            for m in (0, 30):
                time_slots.append(f"{h:02d}:{m:02d}")
        context['time_slots'] = time_slots
        
        return context
    
    def _get_profesional_for_user(self, user):
        """Busca el Empleado vinculado directamente al Usuario."""
        if hasattr(user, 'empleado') and user.empleado and user.empleado.activo:
            return user.empleado
        return None
    
    def post(self, request, *args, **kwargs):
        from turnos.models import Turno, EstadoTurno
        from pacientes.models import Paciente
        from servicios.models import Servicio
        from empleados.models import Empleado
        from django.utils import timezone
        from django.db.models import Q
        from django.contrib import messages
        from datetime import datetime
        
        action = request.POST.get('action')
        if action not in ['crear_turno', 'editar_turno']:
            return self.get(request, *args, **kwargs)
        
        is_editing = action == 'editar_turno'
        turno_id = request.POST.get('turno_id') if is_editing else None
        
        # Leer paciente_id desde el nuevo campo (datalist) o el anterior (select)
        paciente_id = request.POST.get('paciente_id') or request.POST.get('paciente')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        servicio_id = request.POST.get('servicio')
        observaciones = request.POST.get('observaciones', '')
        
        # Validaciones básicas
        if not all([paciente_id, fecha, hora_inicio, hora_fin, servicio_id]):
            messages.error(request, 'Todos los campos obligatorios deben completarse.')
            return self.get(request, *args, **kwargs)
        
        # Validar que la fecha/hora no sea pasada (solo para creación, en edición permitimos mantener si ya pasó)
        if not is_editing:
            try:
                fecha_turno = datetime.strptime(fecha, '%Y-%m-%d').date()
                hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M').time()
                turno_datetime = timezone.make_aware(datetime.combine(fecha_turno, hora_inicio_dt))
                if turno_datetime < timezone.now():
                    messages.error(request, 'No se puede agendar un turno en el pasado.')
                    return self.get(request, *args, **kwargs)
            except ValueError:
                messages.error(request, 'Formato de fecha u hora inválido.')
                return self.get(request, *args, **kwargs)
        
        try:
            paciente = Paciente.objects.get(pk=paciente_id, activo=True)
            servicio = Servicio.objects.get(pk=servicio_id, activo=True)
        except (Paciente.DoesNotExist, Servicio.DoesNotExist):
            messages.error(request, 'Concurrente o servicio no válido.')
            return self.get(request, *args, **kwargs)
        
        # Determinar el profesional
        profesional = None
        user = request.user
        
        if user.is_superuser or user.rol in ['admin', 'recepcionista', 'orientador']:
            profesional_id = request.POST.get('profesional_id') or request.POST.get('profesional')
            if profesional_id:
                try:
                    profesional = Empleado.objects.get(pk=profesional_id, activo=True)
                except Empleado.DoesNotExist:
                    pass
            if not profesional:
                profesional_qs = Empleado.objects.filter(activo=True).order_by('persona__apellido')
                if profesional_qs.exists():
                    profesional = profesional_qs.first()
        elif user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            profesional = self._get_profesional_for_user(user)
        
        if not profesional:
            messages.error(request, 'No se pudo determinar el profesional para el turno. Verifique que su usuario esté vinculado a un empleado.')
            return self.get(request, *args, **kwargs)
        
        # Validar solapamiento de horarios (excluyendo el turno actual si estamos editando)
        solapamiento_qs = Turno.objects.filter(
            profesional=profesional,
            fecha=fecha,
            estado__in=[EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO],
        ).filter(
            Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
        )
        if is_editing and turno_id:
            solapamiento_qs = solapamiento_qs.exclude(pk=turno_id)
        
        if solapamiento_qs.exists():
            messages.error(request, f'El profesional ya tiene un turno en ese horario.')
            return self.get(request, *args, **kwargs)
        
        if is_editing and turno_id:
            # Editar turno existente
            try:
                turno = Turno.objects.get(pk=turno_id)
            except Turno.DoesNotExist:
                messages.error(request, 'Turno no encontrado.')
                return self.get(request, *args, **kwargs)
            
            # Verificar permisos: profesional solo puede editar sus propios turnos
            if user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
                if turno.profesional != profesional:
                    messages.error(request, 'No tiene permiso para editar este turno.')
                    return self.get(request, *args, **kwargs)
            
            turno.paciente = paciente
            turno.profesional = profesional
            turno.servicio = servicio
            turno.fecha = fecha
            turno.hora_inicio = hora_inicio
            turno.hora_fin = hora_fin
            turno.observaciones = observaciones
            turno.save()
            
            messages.success(request, f'Turno actualizado exitosamente para {paciente.persona} el {fecha}.')
        else:
            # Crear nuevo turno
            turno = Turno.objects.create(
                paciente=paciente,
                profesional=profesional,
                servicio=servicio,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado=EstadoTurno.PENDIENTE,
                observaciones=observaciones,
            )
            
            messages.success(request, f'Turno agendado exitosamente para {paciente.persona} el {fecha}.')
        
        return self.get(request, *args, **kwargs)


def turnos_disponibilidad(request):
    """
    Endpoint para verificar disponibilidad de horarios para un profesional en una fecha.
    GET /api/turnos/disponibles/?fecha=YYYY-MM-DD&hora_inicio=HH:MM&hora_fin=HH:MM&profesional_id=X
    """
    from turnos.models import Turno, EstadoTurno
    from empleados.models import Empleado
    from django.http import JsonResponse
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    fecha = request.GET.get('fecha')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fin = request.GET.get('hora_fin')
    profesional_id = request.GET.get('profesional_id')
    
    if not all([fecha, hora_inicio, hora_fin, profesional_id]):
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)
    
    try:
        profesional = Empleado.objects.get(pk=profesional_id, activo=True)
    except Empleado.DoesNotExist:
        return JsonResponse({'error': 'Profesional no encontrado'}, status=404)
    
    # Verificar si hay solapamiento
    solapamiento = Turno.objects.filter(
        profesional=profesional,
        fecha=fecha,
        estado__in=[EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO],
    ).filter(
        Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
    ).exists()
    
    if solapamiento:
        # Buscar horarios libres sugeridos en el mismo día
        turnos_ocupados = Turno.objects.filter(
            profesional=profesional,
            fecha=fecha,
            estado__in=[EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO],
        ).order_by('hora_inicio')
        
        # Generar slots de 30 minutos desde 8:00 hasta 20:00
        sugerencias = []
        inicio_dia = datetime.strptime('08:00', '%H:%M')
        fin_dia = datetime.strptime('20:00', '%H:%M')
        duracion = datetime.strptime(hora_fin, '%H:%M') - datetime.strptime(hora_inicio, '%H:%M')
        
        current = inicio_dia
        while current + duracion <= fin_dia:
            slot_inicio = current.strftime('%H:%M')
            slot_fin = (current + duracion).strftime('%H:%M')
            
            # Verificar si este slot está libre
            conflicto = False
            for t in turnos_ocupados:
                if t.hora_inicio < (current + duracion).time() and t.hora_fin > current.time():
                    conflicto = True
                    break
            
            if not conflicto:
                sugerencias.append({'inicio': slot_inicio, 'fin': slot_fin})
                if len(sugerencias) >= 3:
                    break
            
            current += timedelta(minutes=30)
        
        return JsonResponse({
            'disponible': False,
            'mensaje': 'El profesional ya tiene un turno en este horario. Por favor, elegí otro.',
            'sugerencias': sugerencias
        })
    
    return JsonResponse({'disponible': True})


class TurnoUpdateView(LoginRequiredMixin, UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/form.html'
    success_url = reverse_lazy('turnos_list')
    login_url = 'login'
    pk_url_kwarg = 'pk'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol in ['admin', 'recepcionista', 'orientador']:
            return Turno.objects.all()
        if hasattr(user, 'empleado') and user.empleado:
            return Turno.objects.filter(profesional=user.empleado)
        return Turno.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'Turno actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el turno. Verifique los datos.')
        return super().form_invalid(form)


@login_required
@require_POST
def cambiar_estado_turno(request, pk, nuevo_estado):
    from turnos.models import Turno, EstadoTurno
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    
    turno = get_object_or_404(Turno, pk=pk)
    
    # Validar permisos
    user = request.user
    is_admin = user.is_superuser or user.rol in ['admin', 'recepcionista']
    is_profesional = user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']
    
    if not (is_admin or (is_profesional and hasattr(user, 'empleado') and user.empleado and turno.profesional == user.empleado)):
        messages.error(request, 'No tiene permiso para cambiar el estado de este turno.')
        return redirect('turnos_list')
    
    # Validar estado
    estados_validos = [EstadoTurno.REALIZADO, EstadoTurno.CANCELADO, EstadoTurno.AUSENTE]
    if nuevo_estado not in estados_validos:
        messages.error(request, 'Estado no válido.')
        return redirect('turnos_list')
    
    # No permitir cambiar estado si ya está finalizado
    if turno.estado in [EstadoTurno.REALIZADO, EstadoTurno.CANCELADO, EstadoTurno.AUSENTE]:
        messages.error(request, 'No se puede cambiar el estado de un turno ya finalizado.')
        return redirect('turnos_list')
    
    turno.estado = nuevo_estado
    turno.save(update_fields=['estado'])
    
    messages.success(request, f'Turno marcado como {turno.get_estado_display().lower()}.')
    return redirect('turnos_list')


class TratamientosListView(LoginRequiredMixin, TemplateView):
    template_name = 'tratamientos/list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from tratamientos.models import PlanTratamiento
        user = self.request.user
        
        base_qs = PlanTratamiento.objects.select_related('paciente__persona').filter(activo=True).order_by('-fecha_inicio')
        
        if user.is_superuser or user.rol in ['admin', 'orientador', 'recepcionista']:
            context['tratamientos'] = base_qs
        elif user.rol in ['psicologo', 'medico', 'trabajador_social', 'kinesiologo', 'psicomotricista', 'nutricionista', 'psicopedagogo', 'pedagogo', 'enfermero']:
            # Profesional: ver planes de sus pacientes (turnos asignados O área)
            profesional_qs = PlanTratamiento.objects.none()
            if user.email:
                from personas.models import Email
                empleado_personas = Email.objects.filter(
                    direccion_email=user.email, activo=True
                ).values_list('persona_id', flat=True)
                if empleado_personas:
                    # Pacientes con turnos asignados a este profesional
                    paciente_ids = Paciente.objects.filter(
                        turnos__profesional__persona_id__in=empleado_personas
                    ).values_list('id', flat=True).distinct()
                    if paciente_ids:
                        profesional_qs = base_qs.filter(paciente_id__in=paciente_ids)
            
            # También incluir planes de pacientes en su área
            area_qs = PlanTratamiento.objects.none()
            if user.area:
                area_qs = base_qs.filter(
                    models.Q(paciente__diagnosticos_area__activo=True, paciente__diagnosticos_area__area=user.area) |
                    models.Q(paciente__seguimientos_trimestrales__activo=True, paciente__seguimientos_trimestrales__area=user.area)
                ).distinct()
            
            # Unir ambos
            if profesional_qs and area_qs:
                context['tratamientos'] = (profesional_qs | area_qs).distinct()
            elif profesional_qs:
                context['tratamientos'] = profesional_qs
            elif area_qs:
                context['tratamientos'] = area_qs
            else:
                context['tratamientos'] = PlanTratamiento.objects.none()
        else:
            context['tratamientos'] = PlanTratamiento.objects.none()
        return context


class EmpleadosListView(SoloAdminMixin, LoginRequiredMixin, TemplateView):
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


class ComprasListView(SoloAdminMixin, LoginRequiredMixin, TemplateView):
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

class EmpleadoCreateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
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


class EmpleadoUpdateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
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


class EmpleadoDeleteView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
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
# DOCUMENTOS CRUD (HTML)
# ============================================================

class DocumentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = DocumentoForm
    template_name = 'documentos/form.html'
    success_url = reverse_lazy('documentos_list')
    login_url = 'login'
    permission_required = 'documentos.add_documento'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('documentos.add_documento',)

    def form_valid(self, form):
        messages.success(self.request, 'Documento creado exitosamente.')
        return super().form_valid(form)


class DocumentoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = DocumentoForm
    template_name = 'documentos/form.html'
    success_url = reverse_lazy('documentos_list')
    login_url = 'login'
    permission_required = 'documentos.change_documento'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('documentos.change_documento',)

    def get_object(self, queryset=None):
        from documentos.models import Documento
        return Documento.objects.filter(activo=True).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Documento actualizado exitosamente.')
        return super().form_valid(form)


class DocumentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'documentos/confirm_delete.html'
    success_url = reverse_lazy('documentos_list')
    login_url = 'login'
    permission_required = 'documentos.delete_documento'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('documentos.delete_documento',)

    def get_object(self, queryset=None):
        from documentos.models import Documento
        return Documento.objects.filter(activo=True).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Documento dado de baja exitosamente.')
        return redirect(self.success_url)


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


# ============================================================
# PROVEEDORES CRUD (HTML)
# ============================================================

class ProveedoresListView(SoloAdminMixin, LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'proveedores/list.html'
    context_object_name = 'proveedores'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return Proveedor.objects.filter(activo=True).order_by('razon_social')


class ProveedorCreateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = ProveedorForm
    template_name = 'proveedores/form.html'
    success_url = reverse_lazy('proveedores_list')
    login_url = 'login'
    permission_required = 'compras.add_proveedor'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.add_proveedor',)

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado exitosamente.')
        return super().form_valid(form)


class ProveedorUpdateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = ProveedorForm
    template_name = 'proveedores/form.html'
    success_url = reverse_lazy('proveedores_list')
    login_url = 'login'
    permission_required = 'compras.change_proveedor'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.change_proveedor',)

    def get_object(self, queryset=None):
        return Proveedor.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado exitosamente.')
        return super().form_valid(form)


class ProveedorDeleteView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'proveedores/confirm_delete.html'
    success_url = reverse_lazy('proveedores_list')
    login_url = 'login'
    permission_required = 'compras.delete_proveedor'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.delete_proveedor',)

    def get_object(self, queryset=None):
        return Proveedor.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Proveedor dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# TIPOS DE GASTO CRUD (HTML)
# ============================================================

class TiposGastoListView(SoloAdminMixin, LoginRequiredMixin, ListView):
    model = TipoGasto
    template_name = 'tipos_gasto/list.html'
    context_object_name = 'tipos_gasto'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return TipoGasto.objects.filter(activo=True).order_by('nombre')


class TipoGastoCreateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = TipoGastoForm
    template_name = 'tipos_gasto/form.html'
    success_url = reverse_lazy('tipos_gasto_list')
    login_url = 'login'
    permission_required = 'compras.add_tipogasto'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.add_tipogasto',)

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de gasto creado exitosamente.')
        return super().form_valid(form)


class TipoGastoUpdateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = TipoGastoForm
    template_name = 'tipos_gasto/form.html'
    success_url = reverse_lazy('tipos_gasto_list')
    login_url = 'login'
    permission_required = 'compras.change_tipogasto'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.change_tipogasto',)

    def get_object(self, queryset=None):
        return TipoGasto.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Tipo de gasto actualizado exitosamente.')
        return super().form_valid(form)


class TipoGastoDeleteView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'tipos_gasto/confirm_delete.html'
    success_url = reverse_lazy('tipos_gasto_list')
    login_url = 'login'
    permission_required = 'compras.delete_tipogasto'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.delete_tipogasto',)

    def get_object(self, queryset=None):
        return TipoGasto.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Tipo de gasto dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# COMPRAS CRUD (HTML)
# ============================================================

class ComprasListView(SoloAdminMixin, LoginRequiredMixin, ListView):
    model = Compra
    template_name = 'compras/list.html'
    context_object_name = 'compras'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return Compra.objects.filter(anulada=False).select_related('proveedor').order_by('-fecha')


class CompraCreateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = CompraForm
    template_name = 'compras/form.html'
    success_url = reverse_lazy('compras_list')
    login_url = 'login'
    permission_required = 'compras.add_compra'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.add_compra',)

    def form_valid(self, form):
        messages.success(self.request, 'Compra creada exitosamente.')
        return super().form_valid(form)


class CompraUpdateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = CompraForm
    template_name = 'compras/form.html'
    success_url = reverse_lazy('compras_list')
    login_url = 'login'
    permission_required = 'compras.change_compra'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.change_compra',)

    def get_object(self, queryset=None):
        return Compra.objects.select_related('proveedor').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Compra actualizada exitosamente.')
        return super().form_valid(form)


class CompraDeleteView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'compras/confirm_delete.html'
    success_url = reverse_lazy('compras_list')
    login_url = 'login'
    permission_required = 'compras.delete_compra'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.delete_compra',)

    def get_object(self, queryset=None):
        return Compra.objects.select_related('proveedor').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.anulada = True
        self.object.save()
        messages.success(self.request, 'Compra anulada exitosamente.')
        return redirect(self.success_url)


# ============================================================
# GASTOS CRUD (HTML)
# ============================================================

class GastosListView(SoloAdminMixin, LoginRequiredMixin, ListView):
    model = Gasto
    template_name = 'gastos/list.html'
    context_object_name = 'gastos'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return Gasto.objects.filter(anulado=False).select_related('tipo_gasto', 'proveedor').order_by('-fecha')


class GastoCreateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = GastoForm
    template_name = 'gastos/form.html'
    success_url = reverse_lazy('gastos_list')
    login_url = 'login'
    permission_required = 'compras.add_gasto'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.add_gasto',)

    def form_valid(self, form):
        messages.success(self.request, 'Gasto creado exitosamente.')
        return super().form_valid(form)


class GastoUpdateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = GastoForm
    template_name = 'gastos/form.html'
    success_url = reverse_lazy('gastos_list')
    login_url = 'login'
    permission_required = 'compras.change_gasto'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.change_gasto',)

    def get_object(self, queryset=None):
        return Gasto.objects.select_related('tipo_gasto', 'proveedor').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Gasto actualizado exitosamente.')
        return super().form_valid(form)


class GastoDeleteView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'gastos/confirm_delete.html'
    success_url = reverse_lazy('gastos_list')
    login_url = 'login'
    permission_required = 'compras.delete_gasto'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('compras.delete_gasto',)

    def get_object(self, queryset=None):
        return Gasto.objects.select_related('tipo_gasto', 'proveedor').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.anulado = True
        self.object.save()
        messages.success(self.request, 'Gasto anulado exitosamente.')
        return redirect(self.success_url)


# ============================================================
# PLANES DE TRATAMIENTO CRUD (HTML)
# ============================================================

class PlanesListView(LoginRequiredMixin, ListView):
    model = PlanTratamiento
    template_name = 'planes/list.html'
    context_object_name = 'planes'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio')


class PlanCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = PlanTratamientoForm
    template_name = 'planes/form.html'
    success_url = reverse_lazy('planes_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_plantratamiento'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_plantratamiento',)

    def form_valid(self, form):
        messages.success(self.request, 'Plan de tratamiento creado exitosamente.')
        return super().form_valid(form)


class PlanUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = PlanTratamientoForm
    template_name = 'planes/form.html'
    success_url = reverse_lazy('planes_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_plantratamiento'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_plantratamiento',)

    def get_object(self, queryset=None):
        return PlanTratamiento.objects.select_related('paciente__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Plan de tratamiento actualizado exitosamente.')
        return super().form_valid(form)


class PlanDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'planes/confirm_delete.html'
    success_url = reverse_lazy('planes_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_plantratamiento'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_plantratamiento',)

    def get_object(self, queryset=None):
        return PlanTratamiento.objects.select_related('paciente__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Plan de tratamiento dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# OBJETIVOS DE TRATAMIENTO CRUD (HTML)
# ============================================================

class ObjetivosListView(LoginRequiredMixin, ListView):
    model = ObjetivoTratamiento
    template_name = 'objetivos/list.html'
    context_object_name = 'objetivos'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return ObjetivoTratamiento.objects.filter(activo=True).select_related('plan_tratamiento__paciente__persona').order_by('-fecha_creacion')


class ObjetivoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = ObjetivoTratamientoForm
    template_name = 'objetivos/form.html'
    success_url = reverse_lazy('objetivos_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_objetivotratamiento'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_objetivotratamiento',)

    def form_valid(self, form):
        messages.success(self.request, 'Objetivo de tratamiento creado exitosamente.')
        return super().form_valid(form)


class ObjetivoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = ObjetivoTratamientoForm
    template_name = 'objetivos/form.html'
    success_url = reverse_lazy('objetivos_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_objetivotratamiento'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_objetivotratamiento',)

    def get_object(self, queryset=None):
        return ObjetivoTratamiento.objects.select_related('plan_tratamiento__paciente__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Objetivo de tratamiento actualizado exitosamente.')
        return super().form_valid(form)


class ObjetivoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'objetivos/confirm_delete.html'
    success_url = reverse_lazy('objetivos_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_objetivotratamiento'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_objetivotratamiento',)

    def get_object(self, queryset=None):
        return ObjetivoTratamiento.objects.select_related('plan_tratamiento__paciente__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Objetivo de tratamiento dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# ACTIVIDADES DE PLAN CRUD (HTML)
# ============================================================

class ActividadesListView(LoginRequiredMixin, ListView):
    model = ActividadPlan
    template_name = 'actividades/list.html'
    context_object_name = 'actividades'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return ActividadPlan.objects.filter(activo=True).select_related('plan_tratamiento__paciente__persona', 'servicio__tipo_servicio').order_by('-plan_tratamiento__fecha_inicio')


class ActividadCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = ActividadPlanForm
    template_name = 'actividades/form.html'
    success_url = reverse_lazy('actividades_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_actividadplan'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_actividadplan',)

    def form_valid(self, form):
        messages.success(self.request, 'Actividad de plan creada exitosamente.')
        return super().form_valid(form)


class ActividadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = ActividadPlanForm
    template_name = 'actividades/form.html'
    success_url = reverse_lazy('actividades_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_actividadplan'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_actividadplan',)

    def get_object(self, queryset=None):
        return ActividadPlan.objects.select_related('plan_tratamiento__paciente__persona', 'servicio__tipo_servicio').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Actividad de plan actualizada exitosamente.')
        return super().form_valid(form)


class ActividadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'actividades/confirm_delete.html'
    success_url = reverse_lazy('actividades_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_actividadplan'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_actividadplan',)

    def get_object(self, queryset=None):
        return ActividadPlan.objects.select_related('plan_tratamiento__paciente__persona', 'servicio__tipo_servicio').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Actividad de plan dada de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# HISTORIALES MÉDICOS CRUD (HTML)
# ============================================================

class HistorialesListView(LoginRequiredMixin, ListView):
    model = HistorialMedico
    template_name = 'historiales/list.html'
    context_object_name = 'historiales'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return HistorialMedico.objects.select_related('paciente__persona', 'profesional__persona').order_by('-fecha')


class HistorialCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = HistorialMedicoForm
    template_name = 'historiales/form.html'
    success_url = reverse_lazy('historiales_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_historialmedico'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_historialmedico',)

    def form_valid(self, form):
        messages.success(self.request, 'Historial médico creado exitosamente.')
        return super().form_valid(form)


class HistorialUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = HistorialMedicoForm
    template_name = 'historiales/form.html'
    success_url = reverse_lazy('historiales_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_historialmedico'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_historialmedico',)

    def get_object(self, queryset=None):
        return HistorialMedico.objects.select_related('paciente__persona', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Historial médico actualizado exitosamente.')
        return super().form_valid(form)


class HistorialDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'historiales/confirm_delete.html'
    success_url = reverse_lazy('historiales_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_historialmedico'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_historialmedico',)

    def get_object(self, queryset=None):
        return HistorialMedico.objects.select_related('paciente__persona', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Historial médico dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# EVOLUCIONES SEMANALES CRUD (HTML)
# ============================================================

class EvolucionesListView(LoginRequiredMixin, ListView):
    model = EvolucionSemanal
    template_name = 'evoluciones/list.html'
    context_object_name = 'evoluciones'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return EvolucionSemanal.objects.select_related('paciente__persona', 'plan_tratamiento__paciente__persona', 'profesional__persona').order_by('-fecha')


class EvolucionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = EvolucionSemanalForm
    template_name = 'evoluciones/form.html'
    success_url = reverse_lazy('evoluciones_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_evolucionsemanal'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_evolucionsemanal',)

    def form_valid(self, form):
        messages.success(self.request, 'Evolución semanal creada exitosamente.')
        return super().form_valid(form)


class EvolucionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = EvolucionSemanalForm
    template_name = 'evoluciones/form.html'
    success_url = reverse_lazy('evoluciones_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_evolucionsemanal'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_evolucionsemanal',)

    def get_object(self, queryset=None):
        return EvolucionSemanal.objects.select_related('paciente__persona', 'plan_tratamiento__paciente__persona', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Evolución semanal actualizada exitosamente.')
        return super().form_valid(form)


class EvolucionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'evoluciones/confirm_delete.html'
    success_url = reverse_lazy('evoluciones_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_evolucionsemanal'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_evolucionsemanal',)

    def get_object(self, queryset=None):
        return EvolucionSemanal.objects.select_related('paciente__persona', 'plan_tratamiento__paciente__persona', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Evolución semanal dada de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# REGISTROS DE ACTIVIDAD CRUD (HTML)
# ============================================================

class RegistrosListView(LoginRequiredMixin, ListView):
    model = RegistroActividad
    template_name = 'registros/list.html'
    context_object_name = 'registros'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return RegistroActividad.objects.select_related('paciente__persona', 'actividad__plan_tratamiento__paciente__persona', 'actividad__servicio__tipo_servicio', 'profesional__persona').order_by('-fecha')


class RegistroCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = RegistroActividadForm
    template_name = 'registros/form.html'
    success_url = reverse_lazy('registros_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_registroactividad'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_registroactividad',)

    def form_valid(self, form):
        messages.success(self.request, 'Registro de actividad creado exitosamente.')
        return super().form_valid(form)


class RegistroUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = RegistroActividadForm
    template_name = 'registros/form.html'
    success_url = reverse_lazy('registros_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_registroactividad'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_registroactividad',)

    def get_object(self, queryset=None):
        return RegistroActividad.objects.select_related('paciente__persona', 'actividad__plan_tratamiento__paciente__persona', 'actividad__servicio__tipo_servicio', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Registro de actividad actualizado exitosamente.')
        return super().form_valid(form)


class RegistroDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'registros/confirm_delete.html'
    success_url = reverse_lazy('registros_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_registroactividad'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_registroactividad',)

    def get_object(self, queryset=None):
        return RegistroActividad.objects.select_related('paciente__persona', 'actividad__plan_tratamiento__paciente__persona', 'actividad__servicio__tipo_servicio', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Registro de actividad dado de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# NOTAS IMPORTANTES CRUD (HTML)
# ============================================================

class NotasListView(LoginRequiredMixin, ListView):
    model = NotaImportante
    template_name = 'notas/list.html'
    context_object_name = 'notas'
    paginate_by = 20
    login_url = 'login'

    def get_queryset(self):
        return NotaImportante.objects.select_related('paciente__persona', 'profesional__persona').order_by('-fecha')


class NotaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None
    form_class = NotaImportanteForm
    template_name = 'notas/form.html'
    success_url = reverse_lazy('notas_list')
    login_url = 'login'
    permission_required = 'tratamientos.add_notaimportante'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.add_notaimportante',)

    def form_valid(self, form):
        messages.success(self.request, 'Nota importante creada exitosamente.')
        return super().form_valid(form)


class NotaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = None
    form_class = NotaImportanteForm
    template_name = 'notas/form.html'
    success_url = reverse_lazy('notas_list')
    login_url = 'login'
    permission_required = 'tratamientos.change_notaimportante'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.change_notaimportante',)

    def get_object(self, queryset=None):
        return NotaImportante.objects.select_related('paciente__persona', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Nota importante actualizada exitosamente.')
        return super().form_valid(form)


class NotaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'notas/confirm_delete.html'
    success_url = reverse_lazy('notas_list')
    login_url = 'login'
    permission_required = 'tratamientos.delete_notaimportante'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('tratamientos.delete_notaimportante',)

    def get_object(self, queryset=None):
        return NotaImportante.objects.select_related('paciente__persona', 'profesional__persona').get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Nota importante dada de baja exitosamente.')
        return redirect(self.success_url)


# ============================================================
# USUARIOS CRUD (HTML) - Solo Admin
# ============================================================

class UsuariosListView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    login_url = 'login'
    permission_required = 'usuarios.view_usuario'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('usuarios.view_usuario',)

    def get_queryset(self):
        return Usuario.objects.filter(is_active=True).select_related('area').order_by('-date_joined')


class UsuarioCreateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioAdminForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios_list')
    login_url = 'login'
    permission_required = 'usuarios.add_usuario'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('usuarios.add_usuario',)

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)


class UsuarioUpdateView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioAdminForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios_list')
    login_url = 'login'
    permission_required = 'usuarios.change_usuario'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('usuarios.change_usuario',)

    def get_queryset(self):
        return Usuario.objects.filter(is_active=True)

    def get_object(self, queryset=None):
        return Usuario.objects.filter(is_active=True).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)


class UsuarioDeleteView(SoloAdminMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'usuarios/confirm_delete.html'
    success_url = reverse_lazy('usuarios_list')
    login_url = 'login'
    permission_required = 'usuarios.delete_usuario'
    pk_url_kwarg = 'pk'

    def get_permission_required(self):
        if self.request.user.is_superuser:
            return ()
        return ('usuarios.delete_usuario',)

    def get_queryset(self):
        return Usuario.objects.filter(is_active=True)

    def get_object(self, queryset=None):
        return Usuario.objects.filter(is_active=True).get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, 'Usuario dado de baja exitosamente.')
        return redirect(self.success_url)