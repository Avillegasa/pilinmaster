from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from viviendas.models import Vivienda

@login_required
def viviendas_por_edificio(request, edificio_id):
    """API endpoint para obtener las viviendas de un edificio específico"""
    try:
        # Obtener viviendas activas del edificio
        viviendas = Vivienda.objects.filter(
            edificio_id=edificio_id,
            activo=True
        ).values('id', 'numero', 'piso').order_by('piso', 'numero')
        
        return JsonResponse(list(viviendas), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)