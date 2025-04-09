from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Visita, MovimientoResidente
from .forms import VisitaForm, MovimientoResidenteEntradaForm, MovimientoResidenteSalidaForm

# Vistas de Visitas
class VisitaListView(LoginRequiredMixin, ListView):
    model = Visita
    template_name = 'accesos/visita_list.html'
    context_object_name = 'visitas'
    
    def get_queryset(self):
        return Visita.objects.filter(fecha_hora_salida__isnull=True).order_by('-fecha_hora_entrada')

class VisitaCreateView(LoginRequiredMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'accesos/visita_form.html'
    success_url = reverse_lazy('visita-list')
    
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
        return MovimientoResidente.objects.all().order_by('-fecha_hora_entrada' if '-fecha_hora_entrada' else '-fecha_hora_salida')

class MovimientoResidenteEntradaView(LoginRequiredMixin, CreateView):
    model = MovimientoResidente
    form_class = MovimientoResidenteEntradaForm
    template_name = 'accesos/movimiento_entrada_form.html'
    success_url = reverse_lazy('movimiento-list')

class MovimientoResidenteSalidaView(LoginRequiredMixin, CreateView):
    model = MovimientoResidente
    form_class = MovimientoResidenteSalidaForm
    template_name = 'accesos/movimiento_salida_form.html'
    success_url = reverse_lazy('movimiento-list')