from django.shortcuts import render, redirect
from django.urls import reverse_lazy
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
    
    # Crear un archivo CSV en memoria
    output = StringIO()
    writer = csv.writer(output)
    
    # Dependiendo del tipo de reporte, generamos diferentes datos
    if reporte.tipo == 'ACCESOS':
        writer.writerow(['ID', 'Nombre Visitante', 'Documento', 'Vivienda', 'Fecha Entrada', 'Fecha Salida', 'Duración (horas)'])
        visitas = Visita.objects.filter(
            fecha_hora_entrada__date__gte=reporte.fecha_desde,
            fecha_hora_entrada__date__lte=reporte.fecha_hasta
        )
        
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
    
    elif reporte.tipo == 'RESIDENTES':
        writer.writerow(['ID', 'Nombre', 'Vivienda', 'Es Propietario', 'Fecha Ingreso', 'Vehículos'])
        residentes = Residente.objects.all()
        
        for residente in residentes:
            writer.writerow([
                residente.id,
                f"{residente.usuario.first_name} {residente.usuario.last_name}",
                str(residente.vivienda) if residente.vivienda else 'Sin asignar',
                'Sí' if residente.es_propietario else 'No',
                residente.fecha_ingreso.strftime('%d/%m/%Y'),
                residente.vehiculos
            ])
    
    elif reporte.tipo == 'VIVIENDAS':
        writer.writerow(['ID', 'Edificio', 'Número', 'Piso', 'Metros Cuadrados', 'Habitaciones', 'Baños', 'Estado'])
        viviendas = Vivienda.objects.all()
        
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
    
    # Guardar el archivo generado en el modelo de Reporte
    reporte.archivo.save(
        f"reporte_{reporte.tipo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        ContentFile(output.getvalue().encode('utf-8')),
        save=True
    )
    
    # Redirigir a la descarga del archivo
    return redirect('descargar-reporte', pk=reporte.pk)

@login_required
def descargar_reporte(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    
    if reporte.archivo:
        response = HttpResponse(reporte.archivo.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{reporte.archivo.name.split("/")[-1]}"'
        return response
    
    return redirect('reporte-list')