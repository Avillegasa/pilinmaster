from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib import messages

from usuarios.views import AdminRequiredMixin
from .models import ReporteConfig
from .forms import (
    ReporteConfigForm, ReporteAccesosForm, ReporteResidentesForm, 
    ReporteViviendasForm, ReportePersonalForm, ExportReportForm
)
from .utils import generar_contexto_reporte, generar_respuesta_reporte


class ReporteListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = ReporteConfig
    template_name = 'reportes/reporte_list.html'
    context_object_name = 'reportes'
    
    def get_queryset(self):
        # Filtrar por tipo si se especifica
        tipo = self.request.GET.get('tipo', '')
        queryset = super().get_queryset()
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Ordenar por fecha de creación más reciente
        return queryset.order_by('-es_favorito', '-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = ReporteConfig.TIPOS
        context['tipo_actual'] = self.request.GET.get('tipo', '')
        
        # Agregar contador de reportes por tipo
        context['contadores'] = {
            tipo[0]: ReporteConfig.objects.filter(tipo=tipo[0]).count()
            for tipo in ReporteConfig.TIPOS
        }
        
        # Agregar los reportes favoritos para acceso rápido
        context['favoritos'] = ReporteConfig.objects.filter(es_favorito=True)[:5]
        
        return context


class ReporteCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = ReporteConfig
    template_name = 'reportes/reporte_form.html'
    
    def get_form_class(self):
        # Determinar el formulario a usar según el tipo de reporte
        tipo = self.request.GET.get('tipo', 'ACCESOS')
        
        if tipo == 'RESIDENTES':
            return ReporteResidentesForm
        elif tipo == 'VIVIENDAS':
            return ReporteViviendasForm
        elif tipo == 'PERSONAL':
            return ReportePersonalForm
        else:  # ACCESOS por defecto
            return ReporteAccesosForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_reporte'] = self.request.GET.get('tipo', 'ACCESOS')
        return context
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, "Reporte creado con éxito")
        return reverse('reporte-preview', args=[self.object.pk])


class ReporteUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ReporteConfig
    template_name = 'reportes/reporte_form.html'
    
    def get_form_class(self):
        # Determinar el formulario a usar según el tipo de reporte
        if self.object.tipo == 'RESIDENTES':
            return ReporteResidentesForm
        elif self.object.tipo == 'VIVIENDAS':
            return ReporteViviendasForm
        elif self.object.tipo == 'PERSONAL':
            return ReportePersonalForm
        else:  # ACCESOS por defecto
            return ReporteAccesosForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_reporte'] = self.object.tipo
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Reporte actualizado con éxito")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('reporte-preview', args=[self.object.pk])


class ReporteDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = ReporteConfig
    template_name = 'reportes/reporte_confirm_delete.html'
    success_url = reverse_lazy('reporte-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Reporte eliminado con éxito")
        return super().delete(request, *args, **kwargs)


@login_required
def reporte_preview(request, pk):
    """Vista para previsualizar el reporte y ofrecer opciones de exportación"""
    reporte_config = get_object_or_404(ReporteConfig, pk=pk)
    
    # Crear el formulario de exportación
    if request.method == 'POST':
        export_form = ExportReportForm(request.POST)
        if export_form.is_valid():
            # Generar el contexto del reporte
            contexto = generar_contexto_reporte(reporte_config)
            
            # Exportar según el formato seleccionado
            formato = export_form.cleaned_data['formato']
            incluir_graficos = export_form.cleaned_data['incluir_graficos']
            paginar = export_form.cleaned_data['paginar']
            orientacion = export_form.cleaned_data['orientacion']
            
            # Si es HTML, mostrar la vista previa
            if formato == 'HTML':
                return render(request, 'reportes/reporte_generado.html', contexto)
            
            # Para otros formatos, generar la respuesta
            respuesta = generar_respuesta_reporte(
                reporte_config, 
                contexto, 
                formato, 
                incluir_graficos, 
                paginar, 
                orientacion
            )
            
            return respuesta
    else:
        export_form = ExportReportForm(initial={'formato': reporte_config.formato_preferido})
    
    # Generar el contexto del reporte para la vista previa
    contexto = generar_contexto_reporte(reporte_config)
    contexto['export_form'] = export_form
    
    return render(request, 'reportes/reporte_preview.html', contexto)


@login_required
def reporte_toggle_favorito(request, pk):
    """Vista para marcar/desmarcar un reporte como favorito"""
    reporte = get_object_or_404(ReporteConfig, pk=pk)
    reporte.es_favorito = not reporte.es_favorito
    reporte.save(update_fields=['es_favorito'])
    
    if reporte.es_favorito:
        messages.success(request, "Reporte marcado como favorito")
    else:
        messages.info(request, "Reporte desmarcado como favorito")
    
    # Redirigir de vuelta a la lista o a la vista previa
    next_url = request.GET.get('next', reverse('reporte-list'))
    return redirect(next_url)


@login_required
def reporte_duplicar(request, pk):
    """Vista para duplicar un reporte existente"""
    reporte_original = get_object_or_404(ReporteConfig, pk=pk)
    
    # Crear una copia del reporte
    reporte_nuevo = ReporteConfig.objects.create(
        nombre=f"Copia de {reporte_original.nombre}",
        tipo=reporte_original.tipo,
        fecha_desde=reporte_original.fecha_desde,
        fecha_hasta=reporte_original.fecha_hasta,
        creado_por=request.user,
        filtros=reporte_original.filtros,
        formato_preferido=reporte_original.formato_preferido,
        es_favorito=False  # La copia no es favorita por defecto
    )
    
    messages.success(request, f"Se ha creado una copia del reporte: {reporte_nuevo.nombre}")
    return redirect('reporte-update', pk=reporte_nuevo.pk)