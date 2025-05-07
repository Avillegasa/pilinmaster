from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Visita, MovimientoResidente
from viviendas.models import Residente, Vivienda

@login_required
def historial_visitas(request):
    """API endpoint para obtener el historial de visitas completadas (con salida registrada)"""
    visitas = Visita.objects.filter(fecha_hora_salida__isnull=False).order_by('-fecha_hora_salida')[:100]  # Limitar a las 100 más recientes
    
    data = []
    for visita in visitas:
        data.append({
            'id': visita.id,
            'nombre_visitante': visita.nombre_visitante,
            'documento_visitante': visita.documento_visitante,
            'vivienda_destino': str(visita.vivienda_destino),
            'residente_autoriza': str(visita.residente_autoriza),
            'fecha_hora_entrada': visita.fecha_hora_entrada.isoformat(),
            'fecha_hora_salida': visita.fecha_hora_salida.isoformat() if visita.fecha_hora_salida else None,
            'motivo': visita.motivo,
            'registrado_por': str(visita.registrado_por) if visita.registrado_por else None
        })
    
    return JsonResponse(data, safe=False)

@login_required
def residentes_por_vivienda(request, vivienda_id):
    """API endpoint para obtener los residentes de una vivienda específica (solo activos)"""
    try:
        vivienda = Vivienda.objects.get(pk=vivienda_id)
        residentes = vivienda.residentes.filter(activo=True)
        
        data = []
        for residente in residentes:
            data.append({
                'id': residente.id,
                'nombre': f"{residente.usuario.first_name} {residente.usuario.last_name}",
                'tipo': residente.tipo_residente.nombre,
                'es_propietario': residente.tipo_residente.es_propietario,
                'activo': residente.activo
            })
        
        return JsonResponse(data, safe=False)
    except Vivienda.DoesNotExist:
        return JsonResponse({'error': 'Vivienda no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)