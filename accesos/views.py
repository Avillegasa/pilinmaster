from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Visita, MovimientoResidente
from .forms import VisitaForm, MovimientoResidenteEntradaForm, MovimientoResidenteSalidaForm
from viviendas.models import Residente

# Vistas de Visitas
class VisitaListView(LoginRequiredMixin, ListView):
    model = Visita
    template_name = 'accesos/visita_list.html'
    context_object_name = 'visitas'
    
    def get_queryset(self):
        # Mostrar solo visitas activas (sin salida registrada)
        return Visita.objects.filter(fecha_hora_salida__isnull=True).order_by('-fecha_hora_entrada')
    
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
            form.fields['residente_autoriza'].queryset = Residente.objects.filter(activo=True)
        return form
    
    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)

@login_required
def registrar_salida_visita(request, pk):
    visita = get_object_or_404(Visita, pk=pk)
    visita.fecha_hora_salida = timezone.now()
    visita.save()
    return redirect('visita-list')

# Vistas de Movimientos de Residentes
class MovimientoResidenteListView(LoginRequiredMixin, ListView):
    model = MovimientoResidente
    template_name = 'accesos/movimiento_list.html'
    context_object_name = 'movimientos'
    
    def get_queryset(self):
        # Ordenar por fecha más reciente primero
        return MovimientoResidente.objects.all().order_by('-fecha_hora_entrada' if '-fecha_hora_entrada' else '-fecha_hora_salida')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Contar entradas y salidas
        context['total_entradas'] = MovimientoResidente.objects.filter(fecha_hora_entrada__isnull=False).count()
        context['total_salidas'] = MovimientoResidente.objects.filter(fecha_hora_salida__isnull=False).count()
        
        return context

class MovimientoResidenteEntradaView(LoginRequiredMixin, CreateView):
    model = MovimientoResidente
    form_class = MovimientoResidenteEntradaForm
    template_name = 'accesos/movimiento_entrada_form.html'
    success_url = reverse_lazy('movimiento-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar para mostrar solo residentes activos en el formulario
        if 'residente' in form.fields:
            form.fields['residente'].queryset = Residente.objects.filter(activo=True)
        return form

class MovimientoResidenteSalidaView(LoginRequiredMixin, CreateView):
    model = MovimientoResidente
    form_class = MovimientoResidenteSalidaForm
    template_name = 'accesos/movimiento_salida_form.html'
    success_url = reverse_lazy('movimiento-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar para mostrar solo residentes activos en el formulario
        if 'residente' in form.fields:
            form.fields['residente'].queryset = Residente.objects.filter(activo=True)
        return form