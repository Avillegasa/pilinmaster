# viviendas/api.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Edificio, Vivienda

def viviendas_por_edificio(request, edificio_id):
    """
    Devuelve las viviendas activas de un edificio específico
    """
    edificio = get_object_or_404(Edificio, id=edificio_id)
    
    # Obtener todas las viviendas activas del edificio
    viviendas = Vivienda.objects.filter(
        edificio=edificio,
        activo=True,
        estado='DESOCUPADO'
    ).order_by('piso', 'numero')
    
    data = []
    for vivienda in viviendas:
        data.append({
            'id': vivienda.id,
            'numero': vivienda.numero,
            'piso': vivienda.piso,
            'estado': vivienda.get_estado_display(),
            'estado_code': vivienda.estado,
            'metros_cuadrados': str(vivienda.metros_cuadrados),
            'habitaciones': vivienda.habitaciones,
            'baños': vivienda.baños,
        })
    
    return JsonResponse(data, safe=False)

def pisos_por_edificio(request, edificio_id):
    """
    Devuelve los pisos disponibles en un edificio específico
    """
    edificio = get_object_or_404(Edificio, id=edificio_id)
    
    pisos = Vivienda.objects.filter(
        edificio=edificio,
        activo=True
    ).values_list('piso', flat=True).distinct().order_by('piso')
    
    return JsonResponse(list(pisos), safe=False)

def residentes_por_vivienda(request, vivienda_id):
    """
    Devuelve los residentes de una vivienda específica
    """
    vivienda = get_object_or_404(Vivienda, id=vivienda_id)
    
    residentes = vivienda.residentes.filter(activo=True)
    
    data = []
    for residente in residentes:
        data.append({
            'id': residente.id,
            'nombre_completo': f"{residente.usuario.first_name} {residente.usuario.last_name}",
            'username': residente.usuario.username,
            'email': residente.usuario.email,
            'telefono': residente.usuario.telefono,
            'es_propietario': residente.es_propietario,
            'vehiculos': residente.vehiculos,
            'fecha_ingreso': residente.fecha_ingreso.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse(data, safe=False)