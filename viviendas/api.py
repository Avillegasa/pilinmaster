from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Edificio, Vivienda, Residente

@login_required
def viviendas_por_edificio(request, edificio_id):
    """API endpoint para obtener las viviendas de un edificio específico
    
    Si edificio_id es 0, devuelve todas las viviendas
    """
    try:
        if edificio_id == 0:
            # Devolver todas las viviendas
            viviendas = Vivienda.objects.all().order_by('edificio__nombre', 'piso', 'numero')
        else:
            # Devolver viviendas del edificio especificado
            viviendas = Vivienda.objects.filter(edificio_id=edificio_id).order_by('piso', 'numero')
        
        data = []
        for vivienda in viviendas:
            data.append({
                'id': vivienda.id,
                'numero': vivienda.numero,
                'piso': vivienda.piso,
                'estado': vivienda.estado,
                'edificio_nombre': vivienda.edificio.nombre,
                'residentes_count': vivienda.residentes.count()
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def residentes_por_vivienda(request, vivienda_id):
    """API endpoint para obtener los residentes de una vivienda específica"""
    try:
        vivienda = Vivienda.objects.get(pk=vivienda_id)
        residentes = Residente.objects.filter(vivienda=vivienda).select_related('usuario', 'tipo_residente')
        
        data = []
        for residente in residentes:
            data.append({
                'id': residente.id,
                'nombre': f"{residente.usuario.first_name} {residente.usuario.last_name}",
                'tipo': residente.tipo_residente.nombre,
                'es_propietario': residente.tipo_residente.es_propietario,
                'vehiculos': residente.vehiculos,
                'activo': residente.activo,
                'fecha_ingreso': residente.fecha_ingreso.strftime('%d/%m/%Y')
            })
        
        return JsonResponse(data, safe=False)
    except Vivienda.DoesNotExist:
        return JsonResponse({'error': 'Vivienda no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)