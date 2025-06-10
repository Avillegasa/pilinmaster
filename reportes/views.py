from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Reporte
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ReporteForm
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
from django.conf import settings
from financiero.models import Pago, Gasto
from django.db.models import Sum
import csv
import pandas as pd  # Asegúrate de tener pandas instalado para Excel

# Safe WeasyPrint import - Won't crash if not available
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    weasyprint = None
    WEASYPRINT_AVAILABLE = False
    print("⚠️ WeasyPrint no disponible - Funcionalidad PDF deshabilitada")

class ReporteListView(ListView):
    model = Reporte
    template_name = 'reportes/reporte_list.html'
    context_object_name = 'reportes'

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo = self.request.GET.get('tipo')
        dados_baja = self.request.GET.get('dados_baja')
        solo_activos = self.request.GET.get('solo_activos')

        # Filtrar por tipo si está especificado
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Aplicar filtros de estado
        if dados_baja == '1':
            queryset = queryset.filter(activo=False)
        elif solo_activos == '1':
            queryset = queryset.filter(activo=True)
        # Si ninguno está especificado, muestra todos (activos e inactivos)
        
        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = self.request.GET.get('tipo')
        dados_baja = self.request.GET.get('dados_baja')
        solo_activos = self.request.GET.get('solo_activos')

        # Aplicar los mismos filtros a los favoritos
        favoritos = Reporte.objects.filter(es_favorito=True)
        
        if tipo:
            favoritos = favoritos.filter(tipo=tipo)
            
        if dados_baja == '1':
            favoritos = favoritos.filter(activo=False)
        elif solo_activos == '1':
            favoritos = favoritos.filter(activo=True)

        context['favoritos'] = favoritos.order_by('-fecha_creacion')
        context['tipos'] = [
            ('ACCESOS', 'Accesos'),
            ('RESIDENTES', 'Residentes'),
            ('VIVIENDAS', 'Viviendas'),
            ('PERSONAL', 'Personal'),
            ('FINANCIERO', 'Financiero'),
        ]
        context['tipo_actual'] = tipo
        context['dados_baja'] = dados_baja
        context['solo_activos'] = solo_activos
        
        # Agregar información adicional para el template
        context['filtros_activos'] = bool(tipo or dados_baja or solo_activos)
        
        return context

class ReporteCreateView(CreateView):
    model = Reporte
    form_class = ReporteForm
    template_name = 'reportes/reporte_form.html'
    success_url = reverse_lazy('reporte-list')

    def get_initial(self):
        initial = super().get_initial()
        tipo = self.request.GET.get('tipo')
        if tipo:
            initial['tipo'] = tipo
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_reporte'] = self.request.GET.get('tipo', self.object.tipo if hasattr(self, 'object') and self.object else '')
        return context

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

class ReporteUpdateView(UpdateView):
    model = Reporte
    form_class = ReporteForm
    template_name = 'reportes/reporte_form.html'
    success_url = reverse_lazy('reporte-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_reporte'] = self.object.tipo
        return context

class ReporteDeleteView(DeleteView):
    model = Reporte
    template_name = 'reportes/reporte_confirm_delete.html'
    success_url = reverse_lazy('reporte-list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        return redirect(self.success_url)

def reporte_preview(request, pk):
    from viviendas.models import Residente, Vivienda
    from personal.models import Empleado
    from accesos.models import Visita

    reporte = get_object_or_404(Reporte, pk=pk)
    context = {
        'reporte': reporte,
        'fecha_generacion': timezone.now(),
    }

    if reporte.tipo == 'RESIDENTES':
        residentes = Residente.objects.all()
        context['residentes'] = residentes
        context['total_residentes'] = residentes.count()
        context['activos'] = residentes.filter(activo=True).count()
        context['propietarios'] = residentes.filter(es_propietario=True).count()
        context['inquilinos'] = residentes.filter(es_propietario=False).count()
    elif reporte.tipo == 'VIVIENDAS':
        viviendas = Vivienda.objects.all()
        context['viviendas'] = viviendas
        context['total_viviendas'] = viviendas.count()
        context['ocupadas'] = viviendas.filter(estado='OCUPADO').count()
        context['desocupadas'] = viviendas.filter(estado='DESOCUPADO').count()
        context['mantenimiento'] = viviendas.filter(estado='MANTENIMIENTO').count()
        if context['total_viviendas']:
            context['porcentaje_ocupacion'] = (context['ocupadas'] / context['total_viviendas']) * 100
        else:
            context['porcentaje_ocupacion'] = 0
    elif reporte.tipo == 'ACCESOS':
        visitas = Visita.objects.all()
        context['visitas'] = visitas
        context['total_visitas'] = visitas.count()
        context['visitas_activas'] = visitas.filter(fecha_hora_salida__isnull=True).count()
        context['visitas_finalizadas'] = visitas.filter(fecha_hora_salida__isnull=False).count()
    elif reporte.tipo == 'PERSONAL':
        empleados = Empleado.objects.all()
        context['empleados'] = empleados
        context['total_empleados'] = empleados.count()
        context['activos'] = empleados.filter(activo=True).count()
        context['inactivos'] = empleados.filter(activo=False).count()
    elif reporte.tipo == 'FINANCIERO':
        fecha_desde = reporte.fecha_desde or timezone.now().date().replace(day=1)
        fecha_hasta = reporte.fecha_hasta or timezone.now().date()

        ingresos = Pago.objects.filter(
            estado='VERIFICADO',
            fecha_pago__gte=fecha_desde,
            fecha_pago__lte=fecha_hasta
        )
        total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0

        egresos = Gasto.objects.filter(
            estado='PAGADO',
            fecha__gte=fecha_desde,
            fecha__lte=fecha_hasta
        )
        total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0

        movimientos = []
        for pago in ingresos:
            movimientos.append({
                'fecha': pago.fecha_pago,
                'concepto': 'Ingreso',
                'tipo': 'Ingreso',
                'monto': pago.monto,
            })
        for gasto in egresos:
            movimientos.append({
                'fecha': gasto.fecha,
                'concepto': gasto.concepto,
                'tipo': 'Egreso',
                'monto': gasto.monto,
            })
        movimientos = sorted(movimientos, key=lambda x: x['fecha'], reverse=True)

        balance = total_ingresos - total_egresos

        context['movimientos'] = movimientos
        context['total_ingresos'] = total_ingresos
        context['total_egresos'] = total_egresos
        context['balance'] = balance

    return render(request, 'reportes/reporte_preview.html', context)

def reporte_toggle_favorito(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    reporte.es_favorito = not reporte.es_favorito
    reporte.save()
    return redirect('reporte-list')

def reporte_duplicar(request, pk):
    reporte_original = get_object_or_404(Reporte, pk=pk)
    
    # Crear una copia del reporte
    reporte_copia = Reporte.objects.create(
        nombre=f"{reporte_original.nombre} (Copia)",
        tipo=reporte_original.tipo,
        formato_preferido=reporte_original.formato_preferido,
        fecha_desde=reporte_original.fecha_desde,
        fecha_hasta=reporte_original.fecha_hasta,
        es_favorito=False,  # Las copias no son favoritas por defecto
        puesto=reporte_original.puesto,
        activo=True  # Las copias se crean activas
    )
    
    return redirect('reporte-list')

def reporte_pdf(request, pk):
    # Check if WeasyPrint is available
    if not WEASYPRINT_AVAILABLE:
        messages.error(request, "Funcionalidad PDF no disponible en este sistema. Instale WeasyPrint para usar esta función.")
        return redirect('reporte-list')
    
    from viviendas.models import Residente, Vivienda
    from personal.models import Empleado
    from accesos.models import Visita

    reporte = get_object_or_404(Reporte, pk=pk)
    reporte.ultima_generacion = timezone.now()
    reporte.save(update_fields=['ultima_generacion'])
    context = {
        'reporte': reporte,
        'fecha_generacion': timezone.now(),
        'logo_path': os.path.join(settings.STATIC_ROOT, 'img/logo_ofi.png'),
        'logo_src': get_logo_base64(),
        'es_pdf': True,  # Para que el template sepa que es PDF
    }

    if reporte.tipo == 'RESIDENTES':
        residentes = Residente.objects.all()
        context['residentes'] = residentes
        context['total_residentes'] = residentes.count()
        context['activos'] = residentes.filter(activo=True).count()
        context['inactivos'] = residentes.filter(activo=False).count()
        # Usa el campo es_propietario directamente
        context['propietarios'] = residentes.filter(es_propietario=True).count()
        context['inquilinos'] = residentes.filter(es_propietario=False).count()
        grafico1 = generar_grafico_barras(
            ['Propietarios', 'Inquilinos'],
            [context['propietarios'], context['inquilinos']],
            'Propietarios vs Inquilinos'
        )
        grafico2 = generar_grafico_barras(
            ['Activos', 'Inactivos'],
            [context['activos'], context['inactivos']],
            'Estado de Residentes'
        )
        context['grafico1'] = grafico1
        context['grafico2'] = grafico2

    elif reporte.tipo == 'VIVIENDAS':
        viviendas = Vivienda.objects.all()
        context['viviendas'] = viviendas
        context['total_viviendas'] = viviendas.count()
        context['ocupadas'] = viviendas.filter(estado='OCUPADO').count()
        context['desocupadas'] = viviendas.filter(estado='DESOCUPADO').count()
        # Ejemplo de gráficos
        grafico1 = generar_grafico_barras(
            ['Ocupadas', 'Desocupadas'],
            [context['ocupadas'], context['desocupadas']],
            'Ocupadas vs Desocupadas'
        )
        grafico2 = generar_grafico_barras(
            ['Total'],
            [context['total_viviendas']],
            'Total de Viviendas'
        )
        context['grafico1'] = grafico1
        context['grafico2'] = grafico2

    elif reporte.tipo == 'PERSONAL':
        empleados = Empleado.objects.all()
        context['empleados'] = empleados
        context['total_empleados'] = empleados.count()
        context['activos'] = empleados.filter(activo=True).count()
        context['inactivos'] = empleados.filter(activo=False).count()
        # Ejemplo de gráficos
        grafico1 = generar_grafico_barras(
            ['Activos', 'Inactivos'],
            [context['activos'], context['inactivos']],
            'Estado de Empleados'
        )
        grafico2 = generar_grafico_barras(
            ['Total'],
            [context['total_empleados']],
            'Total de Empleados'
        )
        context['grafico1'] = grafico1
        context['grafico2'] = grafico2

    elif reporte.tipo == 'ACCESOS':
        visitas = Visita.objects.all()
        context['visitas'] = visitas
        context['total_visitas'] = visitas.count()
        context['visitas_activas'] = visitas.filter(fecha_hora_salida__isnull=True).count()
        context['visitas_finalizadas'] = visitas.filter(fecha_hora_salida__isnull=False).count()
        # Ejemplo de gráficos
        grafico1 = generar_grafico_barras(
            ['Activas', 'Finalizadas'],
            [context['visitas_activas'], context['visitas_finalizadas']],
            'Visitas Activas vs Finalizadas'
        )
        grafico2 = generar_grafico_barras(
            ['Total'],
            [context['total_visitas']],
            'Total de Visitas'
        )
        context['grafico1'] = grafico1
        context['grafico2'] = grafico2

    elif reporte.tipo == 'FINANCIERO':
        # Filtra por el período del reporte
        fecha_desde = reporte.fecha_desde or timezone.now().date().replace(day=1)
        fecha_hasta = reporte.fecha_hasta or timezone.now().date()
        
        # Ingresos: pagos verificados en el periodo
        ingresos = Pago.objects.filter(
            estado='VERIFICADO',
            fecha_pago__gte=fecha_desde,
            fecha_pago__lte=fecha_hasta
        )
        total_ingresos = ingresos.aggregate(total=Sum('monto'))['total'] or 0

        # Egresos: gastos pagados en el periodo
        egresos = Gasto.objects.filter(
            estado='PAGADO',
            fecha__gte=fecha_desde,
            fecha__lte=fecha_hasta
        )
        total_egresos = egresos.aggregate(total=Sum('monto'))['total'] or 0

        # Movimientos: lista combinada de ingresos y egresos
        movimientos = []
        for pago in ingresos:
            movimientos.append({
                'fecha': pago.fecha_pago,
                'concepto': 'Ingreso',
                'tipo': 'Ingreso',
                'monto': pago.monto,
            })
        for gasto in egresos:
            movimientos.append({
                'fecha': gasto.fecha,
                'concepto': gasto.concepto,
                'tipo': 'Egreso',
                'monto': gasto.monto,
            })
        # Ordena por fecha descendente
        movimientos = sorted(movimientos, key=lambda x: x['fecha'], reverse=True)

        balance = total_ingresos - total_egresos

        context['movimientos'] = movimientos
        context['total_ingresos'] = total_ingresos
        context['total_egresos'] = total_egresos
        context['balance'] = balance

        grafico1 = generar_grafico_barras(
            ['Ingresos', 'Egresos'],
            [total_ingresos, total_egresos],
            'Ingresos vs Egresos'
        )
        grafico2 = generar_grafico_barras(
            ['Balance'],
            [balance],
            'Balance'
        )
        context['grafico1'] = grafico1
        context['grafico2'] = grafico2

    # Selecciona el template
    template_map = {
        'ACCESOS': 'reportes/pdf/reporte_accesos.html',
        'RESIDENTES': 'reportes/pdf/reporte_residentes.html',
        'VIVIENDAS': 'reportes/pdf/reporte_viviendas.html',
        'PERSONAL': 'reportes/pdf/reporte_personal.html',
        'FINANCIERO': 'reportes/pdf/reporte_financiero.html',
    }
    template = template_map.get(reporte.tipo, 'reportes/pdf/reporte_generico.html')

    try:
        html = render_to_string(template, context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="reporte_{reporte.nombre}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        weasyprint.HTML(string=html).write_pdf(target=response)
        return response
    except Exception as e:
        messages.error(request, f"Error generando PDF: {str(e)}")
        return redirect('reporte-list')

def reporte_reactivar(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    reporte.activo = True
    reporte.save()
    return redirect('reporte-list')

def generar_grafico_barras(labels, values, titulo):
    try:
        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.bar(labels, values, color='#007bff')
        ax.set_title(titulo)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f'data:image/png;base64,{image_base64}'
    except Exception as e:
        print(f"Error generando gráfico: {e}")
        return None
