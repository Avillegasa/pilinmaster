from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Reporte
from django.shortcuts import redirect, render, get_object_or_404
from .forms import ReporteForm
from django.template.loader import render_to_string
from django.http import HttpResponse
import weasyprint
from django.utils import timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
from django.conf import settings

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
    from financiero.models import Pago, Gasto
    
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # Contexto base
    context = {
        'reporte': reporte,
        'fecha_generacion': timezone.now(),
        'today': timezone.now().date(),
    }
    
    # Obtener nombre del edificio si está filtrado
    if reporte.edificio:
        context['nombre_edificio'] = reporte.edificio.nombre
    else:
        context['nombre_edificio'] = 'Todos los edificios'
    
    # Procesamiento según tipo de reporte
    if reporte.tipo == 'RESIDENTES':
        # Filtrar residentes
        residentes = Residente.objects.all()
        if reporte.edificio:
            residentes = residentes.filter(vivienda__edificio=reporte.edificio)
        
        context.update({
            'residentes': residentes[:10],  # Solo primeros 10 para preview
            'total_residentes': residentes.count(),
            'activos': residentes.filter(activo=True).count(),
            'inactivos': residentes.filter(activo=False).count(),
            'propietarios': residentes.filter(es_propietario=True).count(),
            'inquilinos': residentes.filter(es_propietario=False).count(),
        })
        
        # Datos para gráficos
        context['chart_data'] = {
            'tipos_residentes': {
                'titulo': 'Residentes por Tipo',
                'labels': ['Propietarios', 'Inquilinos'],
                'data': [context['propietarios'], context['inquilinos']]
            },
            'propietarios_inquilinos': {
                'titulo': 'Propietarios vs Inquilinos',
                'labels': ['Propietarios', 'Inquilinos'],
                'data': [context['propietarios'], context['inquilinos']]
            },
            'estado_residentes': {
                'titulo': 'Estado de Residentes',
                'labels': ['Activos', 'Inactivos'],
                'data': [context['activos'], context['inactivos']]
            }
        }
    
    elif reporte.tipo == 'VIVIENDAS':
        # Filtrar viviendas
        viviendas = Vivienda.objects.filter(activo=True)
        if reporte.edificio:
            viviendas = viviendas.filter(edificio=reporte.edificio)
        
        ocupadas = viviendas.filter(estado='OCUPADO').count()
        desocupadas = viviendas.filter(estado='DESOCUPADO').count()
        mantenimiento = viviendas.filter(estado='MANTENIMIENTO').count()
        total = viviendas.count()
        
        porcentaje_ocupacion = (ocupadas / total * 100) if total > 0 else 0
        
        context.update({
            'viviendas': viviendas[:10],
            'total_viviendas': total,
            'ocupadas': ocupadas,
            'desocupadas': desocupadas,
            'mantenimiento': mantenimiento,
            'porcentaje_ocupacion': porcentaje_ocupacion,
        })
        
        # Datos para gráficos
        context['chart_data'] = {
            'estado_viviendas': {
                'titulo': 'Estado de Viviendas',
                'labels': ['Ocupadas', 'Desocupadas', 'Mantenimiento'],
                'data': [ocupadas, desocupadas, mantenimiento]
            },
            'viviendas_por_edificio': {
                'titulo': 'Viviendas por Edificio',
                'labels': [reporte.edificio.nombre if reporte.edificio else 'Todos'],
                'data': [total]
            }
        }
    
    elif reporte.tipo == 'PERSONAL':
        # Filtrar personal
        empleados = Empleado.objects.all()
        
        context.update({
            'empleados': empleados[:10],
            'total_empleados': empleados.count(),
            'activos': empleados.filter(activo=True).count(),
            'inactivos': empleados.filter(activo=False).count(),
        })
        
        # Estadísticas por puesto
        from django.db.models import Count
        puestos_stats = empleados.values('puesto__nombre').annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')
        
        context['puestos_stats'] = puestos_stats
        
        # Datos para gráficos
        context['chart_data'] = {
            'empleados_por_puesto': {
                'titulo': 'Empleados por Puesto',
                'labels': [p['puesto__nombre'] for p in puestos_stats],
                'data': [p['cantidad'] for p in puestos_stats]
            },
            'estado_empleados': {
                'titulo': 'Estado de Empleados',
                'labels': ['Activos', 'Inactivos'],
                'data': [context['activos'], context['inactivos']]
            }
        }
    
    elif reporte.tipo == 'ACCESOS':
        # Filtrar visitas
        visitas = Visita.objects.all()
        
        if reporte.fecha_desde:
            visitas = visitas.filter(fecha_hora_entrada__date__gte=reporte.fecha_desde)
        if reporte.fecha_hasta:
            visitas = visitas.filter(fecha_hora_entrada__date__lte=reporte.fecha_hasta)
        if reporte.edificio:
            visitas = visitas.filter(vivienda_destino__edificio=reporte.edificio)
        
        activas = visitas.filter(fecha_hora_salida__isnull=True).count()
        finalizadas = visitas.filter(fecha_hora_salida__isnull=False).count()
        
        context.update({
            'visitas': visitas[:10],
            'total_visitas': visitas.count(),
            'visitas_activas': activas,
            'visitas_finalizadas': finalizadas,
        })
        
        # Calcular duración promedio
        visitas_con_duracion = visitas.filter(fecha_hora_salida__isnull=False)
        if visitas_con_duracion.exists():
            duraciones = []
            for visita in visitas_con_duracion:
                if visita.fecha_hora_salida and visita.fecha_hora_entrada:
                    duracion = visita.fecha_hora_salida - visita.fecha_hora_entrada
                    duraciones.append(duracion.total_seconds() / 3600)  # en horas
            
            if duraciones:
                context['duracion_promedio'] = sum(duraciones) / len(duraciones)
        
        # Datos para gráficos
        context['chart_data'] = {
            'estado_visitas': {
                'titulo': 'Estado de Visitas',
                'labels': ['Activas', 'Finalizadas'],
                'data': [activas, finalizadas]
            },
            'visitas_por_edificio': {
                'titulo': 'Visitas por Edificio',
                'labels': [reporte.edificio.nombre if reporte.edificio else 'Todos'],
                'data': [visitas.count()]
            }
        }
    
    elif reporte.tipo == 'FINANCIERO':
        # Datos financieros
        fecha_desde = reporte.fecha_desde or timezone.now().date().replace(day=1)
        fecha_hasta = reporte.fecha_hasta or timezone.now().date()
        
        # Ingresos (pagos verificados)
        ingresos = Pago.objects.filter(
            estado='VERIFICADO',
            fecha_pago__range=[fecha_desde, fecha_hasta]
        )
        
        # Egresos (gastos pagados)
        egresos = Gasto.objects.filter(
            estado='PAGADO',
            fecha__range=[fecha_desde, fecha_hasta]
        )
        
        total_ingresos = sum(p.monto for p in ingresos)
        total_egresos = sum(g.monto for g in egresos)
        balance = total_ingresos - total_egresos
        
        context.update({
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'balance': balance,
            'ingresos': ingresos[:5],
            'egresos': egresos[:5],
        })
        
        # Datos para gráficos
        context['chart_data'] = {
            'ingresos_egresos': {
                'titulo': 'Ingresos vs Egresos',
                'labels': ['Ingresos', 'Egresos'],
                'data': [float(total_ingresos), float(total_egresos)]
            }
        }
    
    # Exportar form para vista previa
    from .forms import ExportForm
    context['export_form'] = ExportForm()
    
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
    from viviendas.models import Residente, Vivienda
    from personal.models import Empleado
    from accesos.models import Visita

    reporte = get_object_or_404(Reporte, pk=pk)
    context = {
        'reporte': reporte,
        'fecha_generacion': timezone.now(),
        'logo_path': os.path.join(settings.STATIC_ROOT, 'img/logo_ofi.png'),
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
        # Suponiendo que tienes movimientos, ingresos y egresos
        movimientos = []  # Reemplaza por tu queryset real
        total_ingresos = 0
        total_egresos = 0
        balance = 0
        # ...calcula tus datos...
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

    html = render_to_string(template, context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="reporte_{reporte.nombre}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    weasyprint.HTML(string=html).write_pdf(target=response)
    return response

def reporte_reactivar(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    reporte.activo = True
    reporte.save()
    return redirect('reporte-list')

def generar_grafico_barras(labels, values, titulo):
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