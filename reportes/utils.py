import os
import csv
import json
from io import BytesIO, StringIO
from datetime import datetime
import tempfile
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.template.loader import render_to_string

import xlsxwriter
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from accesos.models import Visita, MovimientoResidente
from viviendas.models import Vivienda, Residente, Edificio, TipoResidente
from personal.models import Empleado, Asignacion, Puesto


def generar_contexto_reporte(reporte_config):
    """
    Genera el contexto para la plantilla de reporte basado en el tipo y los filtros
    del objeto ReporteConfig.
    """
    contexto = {
        'reporte': reporte_config,
        'fecha_generacion': timezone.now(),
        'titulo': f"Reporte de {reporte_config.get_tipo_display()}",
    }
    
    # Establecer filtros comunes
    filtros = reporte_config.filtros or {}
    
    # Generar contexto específico según el tipo de reporte
    if reporte_config.tipo == 'ACCESOS':
        contexto.update(generar_contexto_accesos(reporte_config, filtros))
    elif reporte_config.tipo == 'RESIDENTES':
        contexto.update(generar_contexto_residentes(reporte_config, filtros))
    elif reporte_config.tipo == 'VIVIENDAS':
        contexto.update(generar_contexto_viviendas(reporte_config, filtros))
    elif reporte_config.tipo == 'PERSONAL':
        contexto.update(generar_contexto_personal(reporte_config, filtros))
    
    # Actualizar el timestamp de última generación
    reporte_config.ultima_generacion = timezone.now()
    reporte_config.save(update_fields=['ultima_generacion'])
    
    return contexto


def generar_contexto_accesos(reporte_config, filtros):
    """Genera el contexto para reportes de accesos"""
    # Filtrar visitas por rango de fechas
    visitas_query = Visita.objects.filter(
        fecha_hora_entrada__date__gte=reporte_config.fecha_desde,
        fecha_hora_entrada__date__lte=reporte_config.fecha_hasta
    )
    
    # Aplicar filtros adicionales
    if filtros.get('edificio'):
        visitas_query = visitas_query.filter(vivienda_destino__edificio_id=filtros['edificio'])
    
    if filtros.get('tipo_visita') == 'ACTIVA':
        visitas_query = visitas_query.filter(fecha_hora_salida__isnull=True)
    elif filtros.get('tipo_visita') == 'FINALIZADA':
        visitas_query = visitas_query.filter(fecha_hora_salida__isnull=False)
    
    # Ordenar por fecha de entrada
    visitas = visitas_query.order_by('-fecha_hora_entrada')
    
    # Preparar datos para gráficos
    visitas_por_dia = {}
    for visita in visitas:
        fecha = visita.fecha_hora_entrada.date().strftime('%Y-%m-%d')
        if fecha in visitas_por_dia:
            visitas_por_dia[fecha] += 1
        else:
            visitas_por_dia[fecha] = 1
    
    # Preparar datos de movimientos de residentes
    movimientos_query = MovimientoResidente.objects.filter(
        Q(fecha_hora_entrada__date__gte=reporte_config.fecha_desde,
          fecha_hora_entrada__date__lte=reporte_config.fecha_hasta) |
        Q(fecha_hora_salida__date__gte=reporte_config.fecha_desde,
          fecha_hora_salida__date__lte=reporte_config.fecha_hasta)
    )
    
    if filtros.get('edificio'):
        movimientos_query = movimientos_query.filter(
            residente__vivienda__edificio_id=filtros['edificio']
        )
    
    # Estadísticas adicionales
    total_visitas = visitas.count()
    visitas_activas = visitas.filter(fecha_hora_salida__isnull=True).count()
    visitas_finalizadas = visitas.filter(fecha_hora_salida__isnull=False).count()
    duracion_promedio = None
    
    # Calcular duración promedio de visitas
    visitas_con_salida = visitas.filter(fecha_hora_salida__isnull=False)
    if visitas_con_salida.exists():
        suma_duraciones = sum(
            (v.fecha_hora_salida - v.fecha_hora_entrada).total_seconds() / 3600
            for v in visitas_con_salida
        )
        duracion_promedio = round(suma_duraciones / visitas_con_salida.count(), 2)
    
    # Datos para gráfico de visitas por edificio
    if filtros.get('edificio'):
        edificio = Edificio.objects.get(id=filtros['edificio'])
        nombre_edificio = edificio.nombre
    else:
        nombre_edificio = "Todos los edificios"
        
    # Visitas por edificio cuando no se filtra por un edificio específico
    visitas_por_edificio = {}
    if not filtros.get('edificio'):
        for visita in visitas:
            edificio = visita.vivienda_destino.edificio.nombre
            if edificio in visitas_por_edificio:
                visitas_por_edificio[edificio] += 1
            else:
                visitas_por_edificio[edificio] = 1
    
    return {
        'visitas': visitas,
        'total_visitas': total_visitas,
        'visitas_activas': visitas_activas,
        'visitas_finalizadas': visitas_finalizadas,
        'duracion_promedio': duracion_promedio,
        'movimientos': movimientos_query.order_by('-fecha_hora_entrada', '-fecha_hora_salida'),
        'nombre_edificio': nombre_edificio,
        'chart_data': {
            'visitas_por_dia': {
                'labels': list(visitas_por_dia.keys()),
                'data': list(visitas_por_dia.values()),
                'titulo': 'Visitas por día'
            },
            'visitas_por_edificio': {
                'labels': list(visitas_por_edificio.keys()),
                'data': list(visitas_por_edificio.values()),
                'titulo': 'Visitas por edificio'
            } if visitas_por_edificio else None,
            'estado_visitas': {
                'labels': ['Activas', 'Finalizadas'],
                'data': [visitas_activas, visitas_finalizadas],
                'titulo': 'Estado de visitas'
            }
        }
    }


def generar_contexto_residentes(reporte_config, filtros):
    """Genera el contexto para reportes de residentes"""
    # Base query
    residentes_query = Residente.objects.all()
    
    # Aplicar filtros
    if filtros.get('edificio'):
        residentes_query = residentes_query.filter(vivienda__edificio_id=filtros['edificio'])
    
    if filtros.get('tipo_residente'):
        tipo_ids = filtros['tipo_residente']
        residentes_query = residentes_query.filter(tipo_residente_id__in=tipo_ids)
    
    if filtros.get('estado') == 'activo':
        residentes_query = residentes_query.filter(activo=True)
    elif filtros.get('estado') == 'inactivo':
        residentes_query = residentes_query.filter(activo=False)
    
    residentes = residentes_query.select_related('usuario', 'vivienda', 'tipo_residente')
    
    # Estadísticas
    total_residentes = residentes.count()
    propietarios = residentes.filter(tipo_residente__es_propietario=True).count()
    inquilinos = residentes.filter(tipo_residente__es_propietario=False).count()
    activos = residentes.filter(activo=True).count()
    inactivos = residentes.filter(activo=False).count()
    
    # Estadísticas por tipo de residente
    tipos_stats = []
    for tipo in TipoResidente.objects.all():
        count = residentes.filter(tipo_residente=tipo).count()
        if count > 0:
            tipos_stats.append({
                'nombre': tipo.nombre,
                'cantidad': count,
                'es_propietario': tipo.es_propietario
            })
    
    if filtros.get('edificio'):
        edificio = Edificio.objects.get(id=filtros['edificio'])
        nombre_edificio = edificio.nombre
    else:
        nombre_edificio = "Todos los edificios"
    
    # Residentes por edificio cuando no se filtra por un edificio específico
    residentes_por_edificio = {}
    if not filtros.get('edificio'):
        for residente in residentes:
            if residente.vivienda and residente.vivienda.edificio:
                edificio = residente.vivienda.edificio.nombre
                if edificio in residentes_por_edificio:
                    residentes_por_edificio[edificio] += 1
                else:
                    residentes_por_edificio[edificio] = 1
    
    return {
        'residentes': residentes,
        'total_residentes': total_residentes,
        'propietarios': propietarios,
        'inquilinos': inquilinos,
        'activos': activos,
        'inactivos': inactivos,
        'tipos_stats': tipos_stats,
        'nombre_edificio': nombre_edificio,
        'chart_data': {
            'tipos_residentes': {
                'labels': [tipo['nombre'] for tipo in tipos_stats],
                'data': [tipo['cantidad'] for tipo in tipos_stats],
                'titulo': 'Residentes por tipo'
            },
            'propietarios_inquilinos': {
                'labels': ['Propietarios', 'Inquilinos'],
                'data': [propietarios, inquilinos],
                'titulo': 'Distribución de residentes'
            },
            'estado_residentes': {
                'labels': ['Activos', 'Inactivos'],
                'data': [activos, inactivos],
                'titulo': 'Estado de residentes'
            },
            'residentes_por_edificio': {
                'labels': list(residentes_por_edificio.keys()),
                'data': list(residentes_por_edificio.values()),
                'titulo': 'Residentes por edificio'
            } if residentes_por_edificio else None
        }
    }


def generar_contexto_viviendas(reporte_config, filtros):
    """Genera el contexto para reportes de viviendas"""
    # Base query
    viviendas_query = Vivienda.objects.all()
    
    # Aplicar filtros
    if filtros.get('edificio'):
        viviendas_query = viviendas_query.filter(edificio_id=filtros['edificio'])
    
    if filtros.get('estado'):
        viviendas_query = viviendas_query.filter(estado__in=filtros['estado'])
    
    viviendas = viviendas_query.select_related('edificio')
    
    # Estadísticas
    total_viviendas = viviendas.count()
    ocupadas = viviendas.filter(estado='OCUPADO').count()
    desocupadas = viviendas.filter(estado='DESOCUPADO').count()
    mantenimiento = viviendas.filter(estado='MANTENIMIENTO').count()
    
    # Calcular porcentaje de ocupación
    porcentaje_ocupacion = (ocupadas / total_viviendas * 100) if total_viviendas > 0 else 0
    
    # Datos para gráficos por edificio
    if filtros.get('edificio'):
        edificio = Edificio.objects.get(id=filtros['edificio'])
        nombre_edificio = edificio.nombre
        viviendas_por_piso = {}
        for vivienda in viviendas:
            piso = f"Piso {vivienda.piso}"
            if piso in viviendas_por_piso:
                viviendas_por_piso[piso] += 1
            else:
                viviendas_por_piso[piso] = 1
    else:
        nombre_edificio = "Todos los edificios"
        viviendas_por_edificio = {}
        for vivienda in viviendas:
            edificio = vivienda.edificio.nombre
            if edificio in viviendas_por_edificio:
                viviendas_por_edificio[edificio] += 1
            else:
                viviendas_por_edificio[edificio] = 1
    
    # Calcular datos de tamaño de viviendas
    tamanios = [
        {'rango': 'Menos de 50m²', 'count': viviendas.filter(metros_cuadrados__lt=50).count()},
        {'rango': '50-80m²', 'count': viviendas.filter(metros_cuadrados__gte=50, metros_cuadrados__lt=80).count()},
        {'rango': '80-120m²', 'count': viviendas.filter(metros_cuadrados__gte=80, metros_cuadrados__lt=120).count()},
        {'rango': 'Más de 120m²', 'count': viviendas.filter(metros_cuadrados__gte=120).count()}
    ]
    
    return {
        'viviendas': viviendas,
        'total_viviendas': total_viviendas,
        'ocupadas': ocupadas,
        'desocupadas': desocupadas,
        'mantenimiento': mantenimiento,
        'porcentaje_ocupacion': porcentaje_ocupacion,
        'nombre_edificio': nombre_edificio,
        'tamanios': tamanios,
        'chart_data': {
            'estado_viviendas': {
                'labels': ['Ocupadas', 'Desocupadas', 'En Mantenimiento'],
                'data': [ocupadas, desocupadas, mantenimiento],
                'titulo': 'Estado de viviendas'
            },
            'viviendas_por_edificio': {
                'labels': list(viviendas_por_edificio.keys()),
                'data': list(viviendas_por_edificio.values()),
                'titulo': 'Viviendas por edificio'
            } if not filtros.get('edificio') else None,
            'viviendas_por_piso': {
                'labels': list(viviendas_por_piso.keys()),
                'data': list(viviendas_por_piso.values()),
                'titulo': f'Distribución por piso - {nombre_edificio}'
            } if filtros.get('edificio') else None,
            'tamanios_viviendas': {
                'labels': [t['rango'] for t in tamanios],
                'data': [t['count'] for t in tamanios],
                'titulo': 'Distribución por tamaño'
            }
        }
    }


def generar_contexto_personal(reporte_config, filtros):
    """Genera el contexto para reportes de personal"""
    # Base query
    empleados_query = Empleado.objects.all()
    
    # Aplicar filtros
    if filtros.get('puesto'):
        empleados_query = empleados_query.filter(puesto_id__in=filtros['puesto'])
    
    if filtros.get('estado') == 'activo':
        empleados_query = empleados_query.filter(activo=True)
    elif filtros.get('estado') == 'inactivo':
        empleados_query = empleados_query.filter(activo=False)
    
    empleados = empleados_query.select_related('usuario', 'puesto')
    
    # Estadísticas
    total_empleados = empleados.count()
    activos = empleados.filter(activo=True).count()
    inactivos = empleados.filter(activo=False).count()
    
    # Tareas asignadas en el periodo
    asignaciones = Asignacion.objects.filter(
        fecha_inicio__gte=reporte_config.fecha_desde,
        fecha_inicio__lte=reporte_config.fecha_hasta,
        empleado__in=empleados
    )
    
    # Estadísticas por puesto
    puestos_stats = []
    for puesto in Puesto.objects.all():
        count = empleados.filter(puesto=puesto).count()
        if count > 0:
            puestos_stats.append({
                'nombre': puesto.nombre,
                'cantidad': count
            })
    
    # Estadísticas por tipo de contrato
    contratos_stats = {}
    for empleado in empleados:
        tipo = empleado.get_tipo_contrato_display()
        if tipo in contratos_stats:
            contratos_stats[tipo] += 1
        else:
            contratos_stats[tipo] = 1
    
    return {
        'empleados': empleados,
        'total_empleados': total_empleados,
        'activos': activos,
        'inactivos': inactivos,
        'asignaciones': asignaciones,
        'puestos_stats': puestos_stats,
        'chart_data': {
            'empleados_por_puesto': {
                'labels': [puesto['nombre'] for puesto in puestos_stats],
                'data': [puesto['cantidad'] for puesto in puestos_stats],
                'titulo': 'Empleados por puesto'
            },
            'estado_empleados': {
                'labels': ['Activos', 'Inactivos'],
                'data': [activos, inactivos],
                'titulo': 'Estado de empleados'
            },
            'tipo_contrato': {
                'labels': list(contratos_stats.keys()),
                'data': list(contratos_stats.values()),
                'titulo': 'Tipo de contrato'
            }
        }
    }


def exportar_reporte_csv(reporte_config, contexto):
    """Exporta el reporte en formato CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    if reporte_config.tipo == 'ACCESOS':
        # Cabecera
        writer.writerow(['ID', 'Nombre Visitante', 'Documento', 'Vivienda', 'Fecha Entrada', 'Fecha Salida', 'Duración (horas)'])
        
        # Datos
        for visita in contexto['visitas']:
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
    
    elif reporte_config.tipo == 'RESIDENTES':
        # Cabecera
        writer.writerow(['ID', 'Nombre', 'Vivienda', 'Tipo', 'Es Propietario', 'Fecha Ingreso', 'Estado'])
        
        # Datos
        for residente in contexto['residentes']:
            writer.writerow([
                residente.id,
                f"{residente.usuario.first_name} {residente.usuario.last_name}",
                str(residente.vivienda) if residente.vivienda else 'Sin asignar',
                residente.tipo_residente.nombre,
                'Sí' if residente.tipo_residente.es_propietario else 'No',
                residente.fecha_ingreso.strftime('%d/%m/%Y'),
                'Activo' if residente.activo else 'Inactivo'
            ])
    
    elif reporte_config.tipo == 'VIVIENDAS':
        # Cabecera
        writer.writerow(['ID', 'Edificio', 'Número', 'Piso', 'Metros Cuadrados', 'Habitaciones', 'Baños', 'Estado'])
        
        # Datos
        for vivienda in contexto['viviendas']:
            writer.writerow([
                vivienda.id,
                vivienda.edificio.nombre,
                vivienda.numero,
                vivienda.piso,
                vivienda.metros_cuadrados,
                vivienda.habitaciones,
                vivienda.baños,
                vivienda.get_estado_display()
            ])
            
    elif reporte_config.tipo == 'PERSONAL':
        # Cabecera
        writer.writerow(['ID', 'Nombre', 'Puesto', 'Tipo Contrato', 'Fecha Contratación', 'Especialidad', 'Estado'])
        
        # Datos
        for empleado in contexto['empleados']:
            writer.writerow([
                empleado.id,
                f"{empleado.usuario.first_name} {empleado.usuario.last_name}",
                empleado.puesto.nombre,
                empleado.get_tipo_contrato_display(),
                empleado.fecha_contratacion.strftime('%d/%m/%Y'),
                empleado.especialidad or 'No especificada',
                'Activo' if empleado.activo else 'Inactivo'
            ])
    
    # Devolver CSV como string
    return output.getvalue()


def exportar_reporte_excel(reporte_config, contexto):
    """Exporta el reporte en formato Excel"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Crear estilos
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#4472C4',
        'font_color': 'white'
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy hh:mm',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Hoja principal con datos
    worksheet = workbook.add_worksheet("Datos")
    
    # Título del reporte
    titulo = f"Reporte de {reporte_config.get_tipo_display()} - {reporte_config.nombre}"
    worksheet.merge_range('A1:G1', titulo, title_format)
    worksheet.merge_range('A2:G2', f"Período: {reporte_config.fecha_desde.strftime('%d/%m/%Y')} - {reporte_config.fecha_hasta.strftime('%d/%m/%Y')}", header_format)
    worksheet.merge_range('A3:G3', f"Generado el: {contexto['fecha_generacion'].strftime('%d/%m/%Y %H:%M')}", header_format)
    
    # Agregar datos según el tipo de reporte
    if reporte_config.tipo == 'ACCESOS':
        # Encabezados
        headers = ['ID', 'Nombre Visitante', 'Documento', 'Vivienda', 'Entrada', 'Salida', 'Duración (h)']
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Ajustar anchos de columna
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:F', 18)
        worksheet.set_column('G:G', 12)
        
        # Datos
        for row, visita in enumerate(contexto['visitas'], start=5):
            duracion = ''
            if visita.fecha_hora_salida:
                duracion = round((visita.fecha_hora_salida - visita.fecha_hora_entrada).total_seconds() / 3600, 2)
            
            worksheet.write(row, 0, visita.id, cell_format)
            worksheet.write(row, 1, visita.nombre_visitante, cell_format)
            worksheet.write(row, 2, visita.documento_visitante, cell_format)
            worksheet.write(row, 3, str(visita.vivienda_destino), cell_format)
            worksheet.write_datetime(row, 4, visita.fecha_hora_entrada, date_format)
            
            if visita.fecha_hora_salida:
                worksheet.write_datetime(row, 5, visita.fecha_hora_salida, date_format)
                worksheet.write(row, 6, duracion, cell_format)
            else:
                worksheet.write(row, 5, 'Sin salida', cell_format)
                worksheet.write(row, 6, '-', cell_format)
        
        # Agregar una hoja de resumen
        summary = workbook.add_worksheet("Resumen")
        summary.write(0, 0, "Resumen de Accesos", title_format)
        summary.write(1, 0, "Total de visitas:", header_format)
        summary.write(1, 1, contexto['total_visitas'], cell_format)
        summary.write(2, 0, "Visitas activas:", header_format)
        summary.write(2, 1, contexto['visitas_activas'], cell_format)
        summary.write(3, 0, "Visitas finalizadas:", header_format)
        summary.write(3, 1, contexto['visitas_finalizadas'], cell_format)
        if contexto['duracion_promedio']:
            summary.write(4, 0, "Duración promedio (horas):", header_format)
            summary.write(4, 1, contexto['duracion_promedio'], cell_format)
    
    elif reporte_config.tipo == 'RESIDENTES':
        # Encabezados
        headers = ['ID', 'Nombre', 'Vivienda', 'Tipo', 'Es Propietario', 'Fecha Ingreso', 'Estado']
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Ajustar anchos de columna
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 10)
        
        # Datos
        for row, residente in enumerate(contexto['residentes'], start=5):
            worksheet.write(row, 0, residente.id, cell_format)
            worksheet.write(row, 1, f"{residente.usuario.first_name} {residente.usuario.last_name}", cell_format)
            worksheet.write(row, 2, str(residente.vivienda) if residente.vivienda else 'Sin asignar', cell_format)
            worksheet.write(row, 3, residente.tipo_residente.nombre, cell_format)
            worksheet.write(row, 4, 'Sí' if residente.tipo_residente.es_propietario else 'No', cell_format)
            worksheet.write(row, 5, residente.fecha_ingreso.strftime('%d/%m/%Y'), cell_format)
            worksheet.write(row, 6, 'Activo' if residente.activo else 'Inactivo', cell_format)
        
        # Agregar una hoja de resumen
        summary = workbook.add_worksheet("Resumen")
        summary.write(0, 0, "Resumen de Residentes", title_format)
        summary.write(1, 0, "Total de residentes:", header_format)
        summary.write(1, 1, contexto['total_residentes'], cell_format)
        summary.write(2, 0, "Propietarios:", header_format)
        summary.write(2, 1, contexto['propietarios'], cell_format)
        summary.write(3, 0, "Inquilinos:", header_format)
        summary.write(3, 1, contexto['inquilinos'], cell_format)
        summary.write(4, 0, "Activos:", header_format)
        summary.write(4, 1, contexto['activos'], cell_format)
        summary.write(5, 0, "Inactivos:", header_format)
        summary.write(5, 1, contexto['inactivos'], cell_format)
    
    elif reporte_config.tipo == 'VIVIENDAS':
        # Encabezados
        headers = ['ID', 'Edificio', 'Número', 'Piso', 'Metros Cuadrados', 'Habitaciones', 'Baños', 'Estado']
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Ajustar anchos de columna
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 8)
        worksheet.set_column('E:E', 18)
        worksheet.set_column('F:F', 12)
        worksheet.set_column('G:G', 8)
        worksheet.set_column('H:H', 15)
        
        # Datos
        for row, vivienda in enumerate(contexto['viviendas'], start=5):
            worksheet.write(row, 0, vivienda.id, cell_format)
            worksheet.write(row, 1, vivienda.edificio.nombre, cell_format)
            worksheet.write(row, 2, vivienda.numero, cell_format)
            worksheet.write(row, 3, vivienda.piso, cell_format)
            worksheet.write(row, 4, float(vivienda.metros_cuadrados), cell_format)
            worksheet.write(row, 5, vivienda.habitaciones, cell_format)
            worksheet.write(row, 6, vivienda.baños, cell_format)
            worksheet.write(row, 7, vivienda.get_estado_display(), cell_format)
        
        # Agregar una hoja de resumen
        summary = workbook.add_worksheet("Resumen")
        summary.write(0, 0, "Resumen de Viviendas", title_format)
        summary.write(1, 0, "Total de viviendas:", header_format)
        summary.write(1, 1, contexto['total_viviendas'], cell_format)
        summary.write(2, 0, "Ocupadas:", header_format)
        summary.write(2, 1, contexto['ocupadas'], cell_format)
        summary.write(3, 0, "Desocupadas:", header_format)
        summary.write(3, 1, contexto['desocupadas'], cell_format)
        summary.write(4, 0, "En mantenimiento:", header_format)
        summary.write(4, 1, contexto['mantenimiento'], cell_format)
        summary.write(5, 0, "Porcentaje de ocupación:", header_format)
        summary.write(5, 1, f"{contexto['porcentaje_ocupacion']:.2f}%", cell_format)
    
    elif reporte_config.tipo == 'PERSONAL':
        # Encabezados
        headers = ['ID', 'Nombre', 'Puesto', 'Tipo Contrato', 'Fecha Contratación', 'Especialidad', 'Estado']
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Ajustar anchos de columna
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 18)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 10)
        
        # Datos
        for row, empleado in enumerate(contexto['empleados'], start=5):
            worksheet.write(row, 0, empleado.id, cell_format)
            worksheet.write(row, 1, f"{empleado.usuario.first_name} {empleado.usuario.last_name}", cell_format)
            worksheet.write(row, 2, empleado.puesto.nombre, cell_format)
            worksheet.write(row, 3, empleado.get_tipo_contrato_display(), cell_format)
            worksheet.write(row, 4, empleado.fecha_contratacion.strftime('%d/%m/%Y'), cell_format)
            worksheet.write(row, 5, empleado.especialidad or 'No especificada', cell_format)
            worksheet.write(row, 6, 'Activo' if empleado.activo else 'Inactivo', cell_format)
        
        # Agregar una hoja de resumen
        summary = workbook.add_worksheet("Resumen")
        summary.write(0, 0, "Resumen de Personal", title_format)
        summary.write(1, 0, "Total de empleados:", header_format)
        summary.write(1, 1, contexto['total_empleados'], cell_format)
        summary.write(2, 0, "Empleados activos:", header_format)
        summary.write(2, 1, contexto['activos'], cell_format)
        summary.write(3, 0, "Empleados inactivos:", header_format)
        summary.write(3, 1, contexto['inactivos'], cell_format)
    
    workbook.close()
    output.seek(0)
    return output.getvalue()


def exportar_reporte_pdf(reporte_config, contexto, incluir_graficos=True, paginar=True, orientacion='portrait'):
    """Exporta el reporte en formato PDF usando WeasyPrint"""
    # Renderizar plantilla HTML con el contexto
    template_name = f"reportes/pdf/reporte_{reporte_config.tipo.lower()}.html"
    html_string = render_to_string(template_name, {
        **contexto,
        'incluir_graficos': incluir_graficos,
        'paginar': paginar
    })
    
    # Configurar fuentes
    font_config = FontConfiguration()
    
    # Estilos CSS
    css_string = """
    @page {
        size: %s;
        margin: 2cm;
    }
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        line-height: 1.5;
    }
    .header {
        text-align: center;
        margin-bottom: 20px;
    }
    .titulo {
        font-size: 22px;
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
    }
    .subtitulo {
        font-size: 16px;
        color: #555;
        margin-bottom: 10px;
    }
    .fecha {
        font-size: 14px;
        color: #777;
    }
    table {
        width: 100%%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    th {
        background-color: #f2f2f2;
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    td {
        border: 1px solid #ddd;
        padding: 6px;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .resumen {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .grafico {
        text-align: center;
        margin: 20px 0;
    }
    .grafico img {
        max-width: 100%%;
        height: auto;
    }
    .pie-pagina {
        text-align: center;
        font-size: 12px;
        color: #777;
        margin-top: 30px;
        border-top: 1px solid #ddd;
        padding-top: 10px;
    }
    @media print {
        .page-break {
            page-break-after: always;
        }
    }
    """ % orientacion
    
    # Convertir HTML a PDF
    html = HTML(string=html_string)
    css = CSS(string=css_string, font_config=font_config)
    
    # Generar el PDF
    pdf_file = html.write_pdf(stylesheets=[css], font_config=font_config)
    
    return pdf_file


def generar_respuesta_reporte(reporte_config, contexto, formato='PDF', incluir_graficos=True, paginar=True, orientacion='portrait'):
    """Genera la respuesta HTTP apropiada según el formato de reporte solicitado"""
    # Determinar el formato de archivo y el tipo MIME
    if formato == 'PDF':
        contenido = exportar_reporte_pdf(reporte_config, contexto, incluir_graficos, paginar, orientacion)
        content_type = 'application/pdf'
        extension = 'pdf'
    elif formato == 'CSV':
        contenido = exportar_reporte_csv(reporte_config, contexto)
        content_type = 'text/csv'
        extension = 'csv'
    elif formato == 'EXCEL':
        contenido = exportar_reporte_excel(reporte_config, contexto)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'
    else:  # HTML - solo para visualización
        return None  # Se maneja directamente en la vista
    
    # Crear nombre de archivo
    filename = f"{reporte_config.tipo.lower()}_{reporte_config.nombre.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Escribir el contenido en la respuesta
    if formato == 'CSV':
        response.write(contenido)
    else:
        response.write(contenido)