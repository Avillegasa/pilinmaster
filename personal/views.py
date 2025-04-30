from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

from usuarios.views import AdminRequiredMixin
from .models import Puesto, Empleado, Asignacion, ComentarioAsignacion, Vivienda
from .forms import PuestoForm, EmpleadoForm, AsignacionForm, ComentarioAsignacionForm, AsignacionFiltroForm

# Vistas para Puestos
class PuestoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Puesto
    template_name = 'personal/puesto_list.html'
    context_object_name = 'puestos'

class PuestoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Puesto
    form_class = PuestoForm
    template_name = 'personal/puesto_form.html'
    success_url = reverse_lazy('puesto-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Puesto creado exitosamente.')
        return super().form_valid(form)

class PuestoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Puesto
    form_class = PuestoForm
    template_name = 'personal/puesto_form.html'
    success_url = reverse_lazy('puesto-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Puesto actualizado exitosamente.')
        return super().form_valid(form)

class PuestoDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Puesto
    template_name = 'personal/puesto_confirm_delete.html'
    success_url = reverse_lazy('puesto-list')
    
    def form_valid(self, form):
        try:
            self.object.delete()
            messages.success(self.request, 'Puesto eliminado exitosamente.')
        except Exception as e:
            messages.error(self.request, f'No se pudo eliminar el puesto: {str(e)}')
            return redirect('puesto-list')
        return redirect(self.success_url)

# Vistas para Empleados
class EmpleadoListView(LoginRequiredMixin, ListView):
    model = Empleado
    template_name = 'personal/empleado_list.html'
    context_object_name = 'empleados'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por puesto si se especifica
        puesto_id = self.request.GET.get('puesto')
        if puesto_id:
            queryset = queryset.filter(puesto_id=puesto_id)
        
        # Filtrar por estado (activo/inactivo)
        estado = self.request.GET.get('estado')
        if estado:
            activo = estado == 'activo'
            queryset = queryset.filter(activo=activo)
            
        # Filtrar por búsqueda de texto
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(usuario__first_name__icontains=query) | 
                Q(usuario__last_name__icontains=query) |
                Q(puesto__nombre__icontains=query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puestos'] = Puesto.objects.all()
        context['filtro_puesto'] = self.request.GET.get('puesto', '')
        context['filtro_estado'] = self.request.GET.get('estado', '')
        context['query'] = self.request.GET.get('q', '')
        return context

class EmpleadoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'personal/empleado_form.html'
    success_url = reverse_lazy('empleado-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Empleado creado exitosamente.')
        return super().form_valid(form)

class EmpleadoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'personal/empleado_form.html'
    success_url = reverse_lazy('empleado-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Empleado actualizado exitosamente.')
        return super().form_valid(form)

class EmpleadoDetailView(LoginRequiredMixin, DetailView):
    model = Empleado
    template_name = 'personal/empleado_detail.html'
    context_object_name = 'empleado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener las asignaciones del empleado
        empleado = self.get_object()
        context['asignaciones'] = Asignacion.objects.filter(
            empleado=empleado
        ).order_by('-fecha_asignacion')[:10]  # Mostrar las 10 más recientes
        
        # Estadísticas
        context['total_asignaciones'] = Asignacion.objects.filter(empleado=empleado).count()
        context['asignaciones_pendientes'] = Asignacion.objects.filter(
            empleado=empleado, estado='PENDIENTE'
        ).count()
        context['asignaciones_en_progreso'] = Asignacion.objects.filter(
            empleado=empleado, estado='EN_PROGRESO'
        ).count()
        context['asignaciones_completadas'] = Asignacion.objects.filter(
            empleado=empleado, estado='COMPLETADA'
        ).count()
        
        return context

@login_required
def empleado_change_state(request, pk):
    """Vista para activar/desactivar un empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST':
        # Cambiar el estado del empleado
        empleado.activo = not empleado.activo
        empleado.save()
        
        # Cambiar también el estado del usuario asociado
        empleado.usuario.is_active = empleado.activo
        empleado.usuario.save()
        
        estado = "activado" if empleado.activo else "desactivado"
        messages.success(
            request, 
            f'El empleado {empleado.usuario.first_name} {empleado.usuario.last_name} ha sido {estado} exitosamente.'
        )
        return redirect('empleado-list')
    
    return render(request, 'personal/empleado_change_state.html', {'empleado': empleado})

# Vistas para Asignaciones
class AsignacionListView(LoginRequiredMixin, ListView):
    model = Asignacion
    template_name = 'personal/asignacion_list.html'
    context_object_name = 'asignaciones'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Crear formulario de filtro
        self.filtro_form = AsignacionFiltroForm(self.request.GET or None)
        
        # Aplicar filtros si el formulario es válido
        if self.filtro_form.is_valid():
            data = self.filtro_form.cleaned_data
            
            if data.get('empleado'):
                queryset = queryset.filter(empleado=data['empleado'])
            
            if data.get('tipo'):
                queryset = queryset.filter(tipo=data['tipo'])
            
            if data.get('estado'):
                queryset = queryset.filter(estado=data['estado'])
            
            if data.get('edificio'):
                queryset = queryset.filter(edificio=data['edificio'])
            
            if data.get('fecha_desde'):
                queryset = queryset.filter(fecha_inicio__gte=data['fecha_desde'])
            
            if data.get('fecha_hasta'):
                queryset = queryset.filter(fecha_inicio__lte=data['fecha_hasta'])
        
        # Filtro adicional para usuarios que son empleados (ver solo sus propias asignaciones)
        if hasattr(self.request.user, 'empleado') and not self.request.user.rol.nombre == 'Administrador':
            queryset = queryset.filter(empleado=self.request.user.empleado)
        
        return queryset.order_by('-fecha_asignacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = self.filtro_form
        
        # Estadísticas para el dashboard
        context['total_asignaciones'] = self.get_queryset().count()
        context['asignaciones_pendientes'] = self.get_queryset().filter(estado='PENDIENTE').count()
        context['asignaciones_en_progreso'] = self.get_queryset().filter(estado='EN_PROGRESO').count()
        context['asignaciones_completadas'] = self.get_queryset().filter(estado='COMPLETADA').count()
        
        return context

class AsignacionCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Asignacion
    form_class = AsignacionForm
    template_name = 'personal/asignacion_form.html'
    success_url = reverse_lazy('asignacion-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Asignación creada exitosamente.')
        return super().form_valid(form)

class AsignacionUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Asignacion
    form_class = AsignacionForm
    template_name = 'personal/asignacion_form.html'
    success_url = reverse_lazy('asignacion-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Asignación actualizada exitosamente.')
        return super().form_valid(form)

class AsignacionDetailView(LoginRequiredMixin, DetailView):
    model = Asignacion
    template_name = 'personal/asignacion_detail.html'
    context_object_name = 'asignacion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir el formulario de comentarios
        context['comentario_form'] = ComentarioAsignacionForm()
        # Obtener los comentarios para esta asignación
        context['comentarios'] = self.object.comentarios.all().order_by('-fecha')
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejar el envío del formulario de comentarios"""
        self.object = self.get_object()
        form = ComentarioAsignacionForm(request.POST)
        
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.asignacion = self.object
            comentario.usuario = request.user
            comentario.save()
            messages.success(request, 'Comentario añadido exitosamente.')
        
        return redirect('asignacion-detail', pk=self.object.pk)

@login_required
def cambiar_estado_asignacion(request, pk):
    """Vista para cambiar el estado de una asignación"""
    asignacion = get_object_or_404(Asignacion, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in [estado[0] for estado in Asignacion.ESTADOS]:
            # Guardar el estado anterior para el mensaje
            estado_anterior = asignacion.get_estado_display()
            
            # Actualizar el estado
            asignacion.estado = nuevo_estado
            asignacion.save()
            
            # Añadir un comentario automático sobre el cambio de estado
            ComentarioAsignacion.objects.create(
                asignacion=asignacion,
                usuario=request.user,
                comentario=f"Estado cambiado de '{estado_anterior}' a '{asignacion.get_estado_display()}'."
            )
            
            messages.success(request, f'Estado de la asignación cambiado a {asignacion.get_estado_display()}.')
        else:
            messages.error(request, 'Estado no válido.')
        
        return redirect('asignacion-detail', pk=asignacion.pk)
    
    return render(request, 'personal/cambiar_estado_asignacion.html', {
        'asignacion': asignacion,
        'estados': Asignacion.ESTADOS,
    })

# API para actualizar viviendas según el edificio seleccionado
@login_required
def viviendas_por_edificio_api(request):
    edificio_id = request.GET.get('edificio_id')
    
    if not edificio_id:
        return JsonResponse({'error': 'ID de edificio no proporcionado'}, status=400)
    
    try:
        viviendas = Vivienda.objects.filter(edificio_id=edificio_id).order_by('piso', 'numero')
        data = [{'id': v.id, 'numero': v.numero, 'piso': v.piso} for v in viviendas]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)