from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages

from usuarios.views import AdminRequiredMixin
from .models import (
    ConceptoCuota, Cuota, Pago, PagoCuota, 
    CategoriaGasto, Gasto, EstadoCuenta
)

# Este archivo contiene stubs de las vistas que se implementarán en la Etapa 2
# Para la Etapa 1 solo necesitamos que el archivo exista para evitar errores de importación

# Vistas para ConceptoCuota
class ConceptoCuotaListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = ConceptoCuota
    template_name = 'financiero/concepto_list.html'
    context_object_name = 'conceptos'

class ConceptoCuotaCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = ConceptoCuota
    fields = ['nombre', 'descripcion', 'monto_base', 'periodicidad', 'aplica_recargo', 'porcentaje_recargo', 'activo']
    template_name = 'financiero/concepto_form.html'
    success_url = reverse_lazy('concepto-list')

class ConceptoCuotaDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = ConceptoCuota
    template_name = 'financiero/concepto_detail.html'
    context_object_name = 'concepto'

class ConceptoCuotaUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ConceptoCuota
    fields = ['nombre', 'descripcion', 'monto_base', 'periodicidad', 'aplica_recargo', 'porcentaje_recargo', 'activo']
    template_name = 'financiero/concepto_form.html'
    success_url = reverse_lazy('concepto-list')

class ConceptoCuotaDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = ConceptoCuota
    template_name = 'financiero/concepto_confirm_delete.html'
    success_url = reverse_lazy('concepto-list')

# Vistas para Cuota
class CuotaListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Cuota
    template_name = 'financiero/cuota_list.html'
    context_object_name = 'cuotas'

class CuotaCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Cuota
    fields = ['concepto', 'vivienda', 'monto', 'fecha_emision', 'fecha_vencimiento', 'notas']
    template_name = 'financiero/cuota_form.html'
    success_url = reverse_lazy('cuota-list')

class CuotaDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Cuota
    template_name = 'financiero/cuota_detail.html'
    context_object_name = 'cuota'

class CuotaUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Cuota
    fields = ['concepto', 'vivienda', 'monto', 'fecha_emision', 'fecha_vencimiento', 'notas']
    template_name = 'financiero/cuota_form.html'
    success_url = reverse_lazy('cuota-list')

@login_required
def generar_cuotas(request):
    """Vista para generar cuotas masivamente"""
    return redirect('cuota-list')

# Vistas para Pago
class PagoListView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'financiero/pago_list.html'
    context_object_name = 'pagos'

class PagoCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    fields = ['vivienda', 'residente', 'monto', 'fecha_pago', 'metodo_pago', 'referencia', 'comprobante', 'notas']
    template_name = 'financiero/pago_form.html'
    success_url = reverse_lazy('pago-list')

class PagoDetailView(LoginRequiredMixin, DetailView):
    model = Pago
    template_name = 'financiero/pago_detail.html'
    context_object_name = 'pago'

class PagoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pago
    fields = ['vivienda', 'residente', 'monto', 'fecha_pago', 'metodo_pago', 'referencia', 'comprobante', 'notas']
    template_name = 'financiero/pago_form.html'
    success_url = reverse_lazy('pago-list')

@login_required
def verificar_pago(request, pk):
    """Vista para verificar un pago"""
    return redirect('pago-list')

@login_required
def rechazar_pago(request, pk):
    """Vista para rechazar un pago"""
    return redirect('pago-list')

# Vistas para CategoriaGasto
class CategoriaGastoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CategoriaGasto
    template_name = 'financiero/categoria_gasto_list.html'
    context_object_name = 'categorias'

class CategoriaGastoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = CategoriaGasto
    fields = ['nombre', 'descripcion', 'presupuesto_mensual', 'color', 'activo']
    template_name = 'financiero/categoria_gasto_form.html'
    success_url = reverse_lazy('categoria-gasto-list')

class CategoriaGastoDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = CategoriaGasto
    template_name = 'financiero/categoria_gasto_detail.html'
    context_object_name = 'categoria'

class CategoriaGastoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = CategoriaGasto
    fields = ['nombre', 'descripcion', 'presupuesto_mensual', 'color', 'activo']
    template_name = 'financiero/categoria_gasto_form.html'
    success_url = reverse_lazy('categoria-gasto-list')

class CategoriaGastoDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = CategoriaGasto
    template_name = 'financiero/categoria_gasto_confirm_delete.html'
    success_url = reverse_lazy('categoria-gasto-list')

# Vistas para Gasto
class GastoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Gasto
    template_name = 'financiero/gasto_list.html'
    context_object_name = 'gastos'

class GastoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Gasto
    fields = ['categoria', 'concepto', 'descripcion', 'monto', 'fecha', 'proveedor', 
              'factura', 'comprobante', 'estado', 'tipo_gasto', 'presupuestado', 'recurrente', 'notas']
    template_name = 'financiero/gasto_form.html'
    success_url = reverse_lazy('gasto-list')

class GastoDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Gasto
    template_name = 'financiero/gasto_detail.html'
    context_object_name = 'gasto'

class GastoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Gasto
    fields = ['categoria', 'concepto', 'descripcion', 'monto', 'fecha', 'proveedor', 
              'factura', 'comprobante', 'estado', 'tipo_gasto', 'presupuestado', 'recurrente', 'notas']
    template_name = 'financiero/gasto_form.html'
    success_url = reverse_lazy('gasto-list')

@login_required
def marcar_gasto_pagado(request, pk):
    """Vista para marcar un gasto como pagado"""
    return redirect('gasto-list')

@login_required
def cancelar_gasto(request, pk):
    """Vista para cancelar un gasto"""
    return redirect('gasto-list')

# Vistas para EstadoCuenta
class EstadoCuentaListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = EstadoCuenta
    template_name = 'financiero/estado_cuenta_list.html'
    context_object_name = 'estados_cuenta'

class EstadoCuentaCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = EstadoCuenta
    fields = ['vivienda', 'fecha_inicio', 'fecha_fin', 'saldo_anterior']
    template_name = 'financiero/estado_cuenta_form.html'
    success_url = reverse_lazy('estado-cuenta-list')

class EstadoCuentaDetailView(LoginRequiredMixin, DetailView):
    model = EstadoCuenta
    template_name = 'financiero/estado_cuenta_detail.html'
    context_object_name = 'estado_cuenta'

@login_required
def estado_cuenta_pdf(request, pk):
    """Vista para generar PDF de estado de cuenta"""
    return HttpResponse("Función no implementada", content_type="text/plain")

@login_required
def enviar_estado_cuenta(request, pk):
    """Vista para enviar estado de cuenta por email"""
    return redirect('estado-cuenta-list')

@login_required
def generar_estados_cuenta(request):
    """Vista para generar estados de cuenta masivamente"""
    return redirect('estado-cuenta-list')

# Dashboard Financiero
@login_required
def dashboard_financiero(request):
    """Vista para el dashboard financiero"""
    return render(request, 'financiero/dashboard.html')

# APIs
@login_required
def api_cuotas_por_vivienda(request, vivienda_id):
    """API para obtener cuotas por vivienda"""
    return JsonResponse({"cuotas": []})

@login_required
def api_resumen_financiero(request):
    """API para obtener resumen financiero"""
    return JsonResponse({
        "ingresos_mes": 0,
        "gastos_mes": 0,
        "balance_mes": 0,
        "cuotas_pendientes": 0,
        "cuotas_vencidas": 0,
        "total_por_cobrar": 0
    })