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