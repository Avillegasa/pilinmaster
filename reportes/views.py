from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse_lazy, reverse
from django.core.files.base import ContentFile
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
from datetime import datetime
from io import StringIO
from usuarios.views import AdminRequiredMixin
from .models import Reporte
from .forms import ReporteForm
from accesos.models import Visita, MovimientoResidente
from viviendas.models import Vivienda, Residente
import json

from .models import Reporte
from accesos.models import Visita, MovimientoResidente 
from viviendas.models import Vivienda, Residente 

class ReporteListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Reporte
    template_name = 'reportes/reporte_list.html'
    context_object_name = 'reportes'

class ReporteCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Reporte
    form_class = ReporteForm
    template_name = 'reportes/reporte_form.html'
    success_url = reverse_lazy('generar-reporte')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

@login_required
def generar_reporte(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # Obtener datos según el tipo de reporte
    context = {
        'reporte': reporte,
        'fecha_generacion': datetime.now(),
    }
    
    if reporte.tipo == 'ACCESOS':
        # Obtener datos de visitas
        visitas = Visita.objects.filter(
            fecha_hora_entrada__date__gte=reporte.fecha_desde,
            fecha_hora_entrada__date__lte=reporte.fecha_hasta
        ).order_by('fecha_hora_entrada')
        
        context['visitas'] = visitas
        
        # Preparar datos para el gráfico
        visitas_por_dia = {}
        for visita in visitas:
            fecha = visita.fecha_hora_entrada.date().strftime('%Y-%m-%d')
            if fecha in visitas_por_dia:
                visitas_por_dia[fecha] += 1
            else:
                visitas_por_dia[fecha] = 1
        
        # Convertir a formato para el gráfico
        labels = list(visitas_por_dia.keys())
        data = list(visitas_por_dia.values())
        
        context['chart_labels'] = json.dumps(labels)
        context['chart_data'] = json.dumps(data)
        context['chart_title'] = 'Visitas por día'
        
        # También crear CSV para descarga
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Nombre Visitante', 'Documento', 'Vivienda', 'Fecha Entrada', 'Fecha Salida', 'Duración (horas)'])
        
        for visita in visitas:
            duracion = ''
            if visita.fecha_hora_salida:
                duracion = round((visita.fecha_hora_salida - visita.fecha_hora_entrada).total_seconds() / 3600, 2)
            
            writer.writerow([
                visita.id,
                visita.nombre_visitante,
                visita.documento_visitante,
                str(visita.vivienda_destino),
                visita.fecha_hora_entrada.strftime('%d/%m/%Y %H:%M'),
                visita.fecha_hora_salida.strftime('%d/%m/%Y %H:%M') if visita.fecha_hora_salida else 'Sin salida',
                duracion
            ])
        
        # Guardar el archivo CSV
        reporte.archivo.save(
            f"reporte_{reporte.tipo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            ContentFile(output.getvalue().encode('utf-8')),
            save=True
        )
    
    elif reporte.tipo == 'RESIDENTES':
        # Obtener datos de residentes
        residentes = Residente.objects.all()
        context['residentes'] = residentes
        
        # Preparar datos para gráfico de propietarios vs inquilinos
        propietarios = residentes.filter(es_propietario=True).count()
        inquilinos = residentes.filter(es_propietario=False).count()
        
        context['chart_labels'] = json.dumps(['Propietarios', 'Inquilinos'])
        context['chart_data'] = json.dumps([propietarios, inquilinos])
        context['chart_title'] = 'Distribución de Residentes'
        
        # Crear CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Nombre', 'Vivienda', 'Es Propietario', 'Fecha Ingreso', 'Vehículos'])
        
        for residente in residentes:
            writer.writerow([
                residente.id,
                f"{residente.usuario.first_name} {residente.usuario.last_name}",
                str(residente.vivienda) if residente.vivienda else 'Sin asignar',
                'Sí' if residente.es_propietario else 'No',
                residente.fecha_ingreso.strftime('%d/%m/%Y'),
                residente.vehiculos
            ])
        
        reporte.archivo.save(
            f"reporte_{reporte.tipo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            ContentFile(output.getvalue().encode('utf-8')),
            save=True
        )
    
    elif reporte.tipo == 'VIVIENDAS':
        # Obtener datos de viviendas
        viviendas = Vivienda.objects.all()
        context['viviendas'] = viviendas
        
        # Preparar datos para gráfico de estados de viviendas
        ocupadas = viviendas.filter(estado='OCUPADO').count()
        desocupadas = viviendas.filter(estado='DESOCUPADO').count()
        mantenimiento = viviendas.filter(estado='MANTENIMIENTO').count()
        
        context['chart_labels'] = json.dumps(['Ocupadas', 'Desocupadas', 'En Mantenimiento'])
        context['chart_data'] = json.dumps([ocupadas, desocupadas, mantenimiento])
        context['chart_title'] = 'Estado de Viviendas'
        
        # Crear CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Edificio', 'Número', 'Piso', 'Metros Cuadrados', 'Habitaciones', 'Baños', 'Estado'])
        
        for vivienda in viviendas:
            writer.writerow([
                vivienda.id,
                vivienda.edificio.nombre,
                vivienda.numero,
                vivienda.piso,
                vivienda.metros_cuadrados,
                vivienda.habitaciones,
                vivienda.baños,
                vivienda.estado
            ])
        
        reporte.archivo.save(
            f"reporte_{reporte.tipo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            ContentFile(output.getvalue().encode('utf-8')),
            save=True
        )
    
    # Renderizar la plantilla con los datos
    return render(request, 'reportes/reporte_generado.html', context)

@login_required
def descargar_reporte(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    
    if reporte.archivo:
        response = HttpResponse(reporte.archivo.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{reporte.archivo.name.split("/")[-1]}"'
        return response
    
    return redirect('reporte-list')