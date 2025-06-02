from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Edificio, Vivienda, Residente

@login_required
def viviendas_por_edificio(request, edificio_id):
    """API endpoint para obtener las viviendas de un edificio específico
    
    Si edificio_id es 0, devuelve todas las viviendas
    Por defecto devuelve solo viviendas activas, a menos que se especifique
    un parámetro 'incluir_inactivas=1'
    """
    try:
        # Verificar si se deben incluir viviendas inactivas
        incluir_inactivas = request.GET.get('incluir_inactivas', '0') == '1'
        
        # Base query para viviendas activas
        query = Vivienda.objects
        if not incluir_inactivas:
            query = query.filter(activo=True)
        
        if int(edificio_id) == 0:
            # Devolver todas las viviendas (activas por defecto)
            viviendas = query.all().order_by('edificio__nombre', 'piso', 'numero')
        else:
            # Devolver viviendas del edificio especificado (activas por defecto)
            viviendas = query.filter(edificio_id=edificio_id).order_by('piso', 'numero')
        
        data = []
        for vivienda in viviendas:
            data.append({
                'id': vivienda.id,
                'numero': vivienda.numero,
                'piso': vivienda.piso,
                'estado': vivienda.estado,
                'activo': vivienda.activo,
                'edificio_nombre': vivienda.edificio.nombre,
                'residentes_count': vivienda.residentes.count()
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def pisos_por_edificio(request, edificio_id):
    """API endpoint para obtener los pisos disponibles en un edificio específico"""
    try:
        # Si edificio_id es 0, devolver todos los pisos del sistema
        if int(edificio_id) == 0:
            pisos = Vivienda.objects.values_list('piso', flat=True).distinct().order_by('piso')
        else:
            pisos = Vivienda.objects.filter(
                edificio_id=edificio_id
            ).values_list('piso', flat=True).distinct().order_by('piso')
        
        return JsonResponse(list(pisos), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def residentes_por_vivienda(request, vivienda_id):
    """API endpoint para obtener los residentes de una vivienda específica"""
    try:
        vivienda = Vivienda.objects.get(pk=vivienda_id)
        
        # Por defecto solo muestra residentes activos, a menos que se solicite mostrar todos
        mostrar_todos = request.GET.get('mostrar_todos', '0') == '1'
        
        if mostrar_todos:
            residentes = Residente.objects.filter(vivienda=vivienda).select_related('usuario')
        else:
            residentes = Residente.objects.filter(vivienda=vivienda, activo=True).select_related('usuario')
        
        data = []
        for residente in residentes:
            data.append({
                'id': residente.id,
                'nombre': f"{residente.usuario.first_name} {residente.usuario.last_name}",
                'es_propietario': residente.es_propietario,
                'vehiculos': residente.vehiculos,
                'activo': residente.activo,
                'fecha_ingreso': residente.fecha_ingreso.strftime('%d/%m/%Y')
            })
        
        return JsonResponse(data, safe=False)
    except Vivienda.DoesNotExist:
        return JsonResponse({'error': 'Vivienda no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)