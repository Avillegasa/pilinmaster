from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from usuarios.views import AdminRequiredMixin
from .models import Edificio, Vivienda, Residente, TipoResidente
from .forms import EdificioForm, ViviendaForm, ResidenteForm, TipoResidenteForm

# Vistas de Edificios
class EdificioListView(LoginRequiredMixin, ListView):
    model = Edificio
    template_name = 'viviendas/edificio_list.html'
    context_object_name = 'edificios'

class EdificioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Edificio
    form_class = EdificioForm
    template_name = 'viviendas/edificio_form.html'
    success_url = reverse_lazy('edificio-list')

class EdificioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Edificio
    form_class = EdificioForm
    template_name = 'viviendas/edificio_form.html'
    success_url = reverse_lazy('edificio-list')

class EdificioDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Edificio
    template_name = 'viviendas/edificio_confirm_delete.html'
    success_url = reverse_lazy('edificio-list')

class EdificioDetailView(LoginRequiredMixin, DetailView):
    model = Edificio
    template_name = 'viviendas/edificio_detail.html'
    context_object_name = 'edificio'

# Vistas de Viviendas
class ViviendaListView(LoginRequiredMixin, ListView):
    model = Vivienda
    template_name = 'viviendas/vivienda_list.html'
    context_object_name = 'viviendas'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por edificio si se proporciona
        edificio_id = self.request.GET.get('edificio')
        if edificio_id:
            queryset = queryset.filter(edificio_id=edificio_id)
        
        # Filtrar por piso si se proporciona
        piso = self.request.GET.get('piso')
        if piso:
            queryset = queryset.filter(piso=piso)
            
        # Filtrar por estado si se proporciona
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Añadir lista de edificios para el selector de filtro
        context['edificios'] = Edificio.objects.all()
        
        # Añadir los valores actuales del filtro
        context['filtro_edificio'] = self.request.GET.get('edificio', '')
        context['filtro_piso'] = self.request.GET.get('piso', '')
        context['filtro_estado'] = self.request.GET.get('estado', '')
        
        # Añadir lista de pisos disponibles para el selector
        pisos = Vivienda.objects.values_list('piso', flat=True).distinct().order_by('piso')
        context['pisos'] = pisos
        
        # Añadir lista de estados para el selector
        context['estados'] = [estado[0] for estado in Vivienda.ESTADOS]
        
        return context

class ViviendaCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Vivienda
    form_class = ViviendaForm
    template_name = 'viviendas/vivienda_form.html'
    success_url = reverse_lazy('vivienda-list')

class ViviendaUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Vivienda
    form_class = ViviendaForm
    template_name = 'viviendas/vivienda_form.html'
    success_url = reverse_lazy('vivienda-list')

class ViviendaDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Vivienda
    template_name = 'viviendas/vivienda_confirm_delete.html'
    success_url = reverse_lazy('vivienda-list')

class ViviendaDetailView(LoginRequiredMixin, DetailView):
    model = Vivienda
    template_name = 'viviendas/vivienda_detail.html'
    context_object_name = 'vivienda'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los tipos de residentes presentes en esta vivienda
        vivienda = self.get_object()
        tipos_residentes = set()
        for residente in vivienda.residentes.all():
            tipos_residentes.add(residente.tipo_residente.nombre)
        
        context['tipos_residentes'] = list(tipos_residentes)
        
        # Estadísticas de residentes por tipo
        stats_por_tipo = {}
        for residente in vivienda.residentes.all():
            tipo_nombre = residente.tipo_residente.nombre
            if tipo_nombre not in stats_por_tipo:
                stats_por_tipo[tipo_nombre] = {
                    'nombre': tipo_nombre,
                    'total': 0,
                    'activos': 0,
                    'inactivos': 0,
                    'es_propietario': residente.tipo_residente.es_propietario
                }
            
            stats_por_tipo[tipo_nombre]['total'] += 1
            if residente.activo:
                stats_por_tipo[tipo_nombre]['activos'] += 1
            else:
                stats_por_tipo[tipo_nombre]['inactivos'] += 1
        
        context['stats_por_tipo'] = stats_por_tipo.values()
        
        return context

# Vistas de Tipos de Residentes
class TipoResidenteListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = TipoResidente
    template_name = 'viviendas/tipo_residente_list.html'
    context_object_name = 'tipos_residentes'

class TipoResidenteCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = TipoResidente
    form_class = TipoResidenteForm
    template_name = 'viviendas/tipo_residente_form.html'
    success_url = reverse_lazy('tipo-residente-list')

class TipoResidenteUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = TipoResidente
    form_class = TipoResidenteForm
    template_name = 'viviendas/tipo_residente_form.html'
    success_url = reverse_lazy('tipo-residente-list')

class TipoResidenteDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = TipoResidente
    template_name = 'viviendas/tipo_residente_confirm_delete.html'
    success_url = reverse_lazy('tipo-residente-list')

# Vistas de Residentes
class ResidenteListView(LoginRequiredMixin, ListView):
    model = Residente
    template_name = 'viviendas/residente_list.html'
    context_object_name = 'residentes'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por edificio si se proporciona
        edificio_id = self.request.GET.get('edificio')
        if edificio_id:
            queryset = queryset.filter(vivienda__edificio_id=edificio_id)
        
        # Filtrar por vivienda si se proporciona
        vivienda_id = self.request.GET.get('vivienda')
        if vivienda_id:
            queryset = queryset.filter(vivienda_id=vivienda_id)
            
        # Filtrar por tipo de residente si se proporciona
        tipo_id = self.request.GET.get('tipo')
        if tipo_id:
            queryset = queryset.filter(tipo_residente_id=tipo_id)
            
        # Filtrar por estado (activo/inactivo)
        estado = self.request.GET.get('estado')
        if estado:
            activo = estado == 'activo'
            queryset = queryset.filter(activo=activo)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Añadir lista de edificios para el selector de filtro
        context['edificios'] = Edificio.objects.all()
        
        # Añadir lista de viviendas para el selector
        edificio_id = self.request.GET.get('edificio')
        if edificio_id:
            context['viviendas'] = Vivienda.objects.filter(edificio_id=edificio_id)
        else:
            context['viviendas'] = Vivienda.objects.all()
        
        # Añadir lista de tipos de residentes para el selector
        context['tipos_residentes'] = TipoResidente.objects.all()
        
        # Añadir los valores actuales del filtro
        context['filtro_edificio'] = self.request.GET.get('edificio', '')
        context['filtro_vivienda'] = self.request.GET.get('vivienda', '')
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        context['filtro_estado'] = self.request.GET.get('estado', '')
        
        return context

class ResidenteCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Residente
    form_class = ResidenteForm
    template_name = 'viviendas/residente_form.html'
    success_url = reverse_lazy('residente-list')

class ResidenteUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Residente
    form_class = ResidenteForm
    template_name = 'viviendas/residente_form.html'
    success_url = reverse_lazy('residente-list')

class ResidenteDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Residente
    template_name = 'viviendas/residente_confirm_delete.html'
    success_url = reverse_lazy('residente-list')

class ResidenteDetailView(LoginRequiredMixin, DetailView):
    model = Residente
    template_name = 'viviendas/residente_detail.html'
    context_object_name = 'residente'