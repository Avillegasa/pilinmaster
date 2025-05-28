from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from usuarios.views import AdminRequiredMixin
from .models import Edificio, Vivienda, Residente
from .forms import EdificioForm, ViviendaForm, ResidenteForm, ViviendaBajaForm

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

class ViviendaListView(ListView):
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
            try:
                piso_int = int(piso)
                queryset = queryset.filter(piso=piso_int)
            except ValueError:
                pass  # Si no es un número, ignora el filtro
            
        # Filtrar por estado si se proporciona
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por activo/inactivo si se proporciona
        activo = self.request.GET.get('activo')
        if activo:
            activo_bool = activo == 'true'
            queryset = queryset.filter(activo=activo_bool)
        else:
            # Por defecto mostrar solo viviendas activas
            queryset = queryset.filter(activo=True)
            
        # Filtrar por búsqueda de número de vivienda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(numero__icontains=search)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Añadir lista de edificios para el selector de filtro
        context['edificios'] = Edificio.objects.all()
        
        # Añadir los valores actuales del filtro
        context['filtro_edificio'] = self.request.GET.get('edificio', '')
        context['filtro_piso'] = self.request.GET.get('piso', '')
        context['filtro_estado'] = self.request.GET.get('estado', '')
        context['filtro_activo'] = self.request.GET.get('activo', 'true')
        
        # Añadir lista de pisos disponibles para el selector
        pisos = Vivienda.objects.values_list('piso', flat=True).distinct().order_by('piso')
        context['pisos'] = pisos
        
        # Añadir lista de estados para el selector
        context['estados'] = [estado[0] for estado in Vivienda.ESTADOS]
        
        # Contar el total de viviendas activas e inactivas
        context['total_activas'] = Vivienda.objects.filter(activo=True).count()
        context['total_inactivas'] = Vivienda.objects.filter(activo=False).count()
        
        return context

class ViviendaCreateView(CreateView):
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
    
    # En la vista ViviendaDetailView
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener estadísticas de residentes
        vivienda = self.get_object()
        
        # Estadísticas de propietarios e inquilinos
        propietarios = vivienda.residentes.filter(es_propietario=True)
        inquilinos = vivienda.residentes.filter(es_propietario=False)
        
        context['propietarios'] = propietarios
        context['inquilinos'] = inquilinos
        context['propietarios_count'] = propietarios.count()
        context['inquilinos_count'] = inquilinos.count()
        context['propietarios_activos_count'] = propietarios.filter(activo=True).count()
        context['propietarios_inactivos_count'] = propietarios.filter(activo=False).count()
        context['inquilinos_activos_count'] = inquilinos.filter(activo=True).count()
        context['inquilinos_inactivos_count'] = inquilinos.filter(activo=False).count()
        
        return context

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
            
        # Filtrar por propietario/inquilino
        es_propietario = self.request.GET.get('es_propietario')
        if es_propietario:
            es_propietario_bool = es_propietario == 'true'
            queryset = queryset.filter(es_propietario=es_propietario_bool)
            
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
        
        # Añadir los valores actuales del filtro
        context['filtro_edificio'] = self.request.GET.get('edificio', '')
        context['filtro_vivienda'] = self.request.GET.get('vivienda', '')
        context['filtro_es_propietario'] = self.request.GET.get('es_propietario', '')
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

class ViviendaBajaView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    Vista para dar de baja una vivienda en lugar de eliminarla.
    Esta vista permite establecer un motivo de baja y la fecha.
    """
    template_name = 'viviendas/vivienda_baja.html'
    
    def get(self, request, pk):
        vivienda = get_object_or_404(Vivienda, pk=pk)
        
        # Verificar si tiene residentes activos
        residentes_activos = vivienda.residentes.filter(activo=True).count()
        
        form = ViviendaBajaForm(instance=vivienda)
        
        return render(request, self.template_name, {
            'vivienda': vivienda,
            'form': form,
            'residentes_activos': residentes_activos
        })
    
    def post(self, request, pk):
        vivienda = get_object_or_404(Vivienda, pk=pk)
        form = ViviendaBajaForm(request.POST, instance=vivienda)
        
        # Verificar si tiene residentes activos
        residentes_activos = vivienda.residentes.filter(activo=True).count()
        
        if residentes_activos > 0 and not request.POST.get('confirmar_residentes'):
            messages.error(request, "No se puede dar de baja una vivienda con residentes activos. Debe reubicarlos primero.")
            return render(request, self.template_name, {
                'vivienda': vivienda,
                'form': form,
                'residentes_activos': residentes_activos
            })
        
        if form.is_valid():
            # Marcar como inactiva y cambiar estado
            vivienda.activo = False
            vivienda.estado = 'BAJA'
            vivienda.fecha_baja = form.cleaned_data.get('fecha_baja') or timezone.now().date()
            vivienda.motivo_baja = form.cleaned_data.get('motivo_baja')
            vivienda.save()
            
            messages.success(request, f"La vivienda {vivienda.numero} ha sido dada de baja correctamente.")
            return redirect('vivienda-list')
        
        return render(request, self.template_name, {
            'vivienda': vivienda,
            'form': form,
            'residentes_activos': residentes_activos
        })