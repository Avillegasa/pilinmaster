from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Visita, MovimientoResidente
from .forms import VisitaForm, MovimientoResidenteEntradaForm, MovimientoResidenteSalidaForm
from viviendas.models import Residente

# Vistas de Visitas
class VisitaListView(LoginRequiredMixin, ListView):
    model = Visita
    template_name = 'accesos/visita_list.html'
    context_object_name = 'visitas'
    paginate_by = 20
    
    def get_queryset(self):
        # Mostrar solo visitas activas (sin salida registrada) con optimización de consultas
        return Visita.objects.filter(
            fecha_hora_salida__isnull=True
        ).select_related(
            'vivienda_destino__edificio',
            'residente_autoriza__usuario',
            'registrado_por'
        ).order_by('-fecha_hora_entrada')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir contador de visitas históricas (con salida registrada)
        context['visitas_historicas'] = Visita.objects.filter(fecha_hora_salida__isnull=False).count()
        return context

class VisitaCreateView(LoginRequiredMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'accesos/visita_form.html'
    success_url = reverse_lazy('visita-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar para mostrar solo residentes activos en el formulario
        if 'residente_autoriza' in form.fields:
            form.fields['residente_autoriza'].queryset = Residente.objects.filter(
                activo=True
            ).select_related('usuario', 'vivienda')
        return form
    
    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        messages.success(self.request, f'Visita de {form.instance.nombre_visitante} registrada correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)

class VisitaDetailView(LoginRequiredMixin, DetailView):
    model = Visita
    template_name = 'accesos/visita_detail.html'
    context_object_name = 'visita'
    
    def get_object(self):
        return get_object_or_404(
            Visita.objects.select_related(
                'vivienda_destino__edificio',
                'residente_autoriza__usuario',
                'registrado_por'
            ),
            pk=self.kwargs['pk']
        )

@login_required
def registrar_salida_visita(request, pk):
    visita = get_object_or_404(Visita, pk=pk)
    
    if visita.fecha_hora_salida:
        messages.warning(request, f'La visita de {visita.nombre_visitante} ya tiene salida registrada.')
    else:
        visita.fecha_hora_salida = timezone.now()
        visita.save()
        messages.success(request, f'Salida de {visita.nombre_visitante} registrada correctamente.')
    
    return redirect('visita-list')

# Vistas de Movimientos de Residentes
class MovimientoResidenteListView(LoginRequiredMixin, ListView):
    model = MovimientoResidente
    template_name = 'accesos/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 20
    
    def get_queryset(self):
        # Optimizar consultas y ordenar por fecha más reciente
        queryset = MovimientoResidente.objects.select_related(
            'residente__usuario',
            'residente__vivienda__edificio'
        ).order_by('-id')  # Usar ID para ordenamiento consistente
        
        # Filtros opcionales
        residente_id = self.request.GET.get('residente')
        if residente_id:
            queryset = queryset.filter(residente_id=residente_id)
        
        tipo_movimiento = self.request.GET.get('tipo')
        if tipo_movimiento == 'entrada':
            queryset = queryset.filter(fecha_hora_entrada__isnull=False, fecha_hora_salida__isnull=True)
        elif tipo_movimiento == 'salida':
            queryset = queryset.filter(fecha_hora_salida__isnull=False, fecha_hora_entrada__isnull=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Contar entradas y salidas
        context['total_entradas'] = MovimientoResidente.objects.filter(
            fecha_hora_entrada__isnull=False
        ).count()
        context['total_salidas'] = MovimientoResidente.objects.filter(
            fecha_hora_salida__isnull=False
        ).count()
        
        # Añadir residentes para filtro
        context['residentes'] = Residente.objects.filter(
            activo=True
        ).select_related('usuario', 'vivienda')
        
        return context

class MovimientoResidenteDetailView(LoginRequiredMixin, DetailView):
    model = MovimientoResidente
    template_name = 'accesos/movimiento_detail.html'
    context_object_name = 'movimiento'
    
    def get_object(self):
        return get_object_or_404(
            MovimientoResidente.objects.select_related(
                'residente__usuario',
                'residente__vivienda__edificio'
            ),
            pk=self.kwargs['pk']
        )

class MovimientoResidenteEntradaView(LoginRequiredMixin, CreateView):
    model = MovimientoResidente
    form_class = MovimientoResidenteEntradaForm
    template_name = 'accesos/movimiento_entrada_form.html'
    success_url = reverse_lazy('movimiento-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar para mostrar solo residentes activos en el formulario
        if 'residente' in form.fields:
            form.fields['residente'].queryset = Residente.objects.filter(
                activo=True
            ).select_related('usuario', 'vivienda')
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Entrada de {form.instance.residente} registrada correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)

class MovimientoResidenteSalidaView(LoginRequiredMixin, CreateView):
    model = MovimientoResidente
    form_class = MovimientoResidenteSalidaForm
    template_name = 'accesos/movimiento_salida_form.html'
    success_url = reverse_lazy('movimiento-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar para mostrar solo residentes activos en el formulario
        if 'residente' in form.fields:
            form.fields['residente'].queryset = Residente.objects.filter(
                activo=True
            ).select_related('usuario', 'vivienda')
        return form
    
    def form_valid(self, form):
        messages.success(self.request, f'Salida de {form.instance.residente} registrada correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)