from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Count, Q
from viviendas.models import Edificio, Vivienda, Residente, TipoResidente
from accesos.models import Visita, MovimientoResidente

@login_required
def dashboard(request):
    # Obtener el edificio seleccionado (si existe)
    edificio_id = request.GET.get('edificio')
    
    # Obtener todos los edificios para el selector
    edificios = Edificio.objects.all()
    
    # Filtrar viviendas según el edificio seleccionado
    if edificio_id:
        viviendas = Vivienda.objects.filter(edificio_id=edificio_id)
        edificio_seleccionado = int(edificio_id)
        # Obtener el nombre del edificio seleccionado
        edificio_nombre = Edificio.objects.get(id=edificio_id).nombre
    else:
        viviendas = Vivienda.objects.all()
        edificio_seleccionado = None
        edificio_nombre = "Todos los edificios"
    
    # Estadísticas de viviendas
    total_viviendas = viviendas.count()
    viviendas_ocupadas = viviendas.filter(estado='OCUPADO').count()
    viviendas_desocupadas = viviendas.filter(estado='DESOCUPADO').count()
    viviendas_mantenimiento = viviendas.filter(estado='MANTENIMIENTO').count()
    
    # Calcular porcentaje de ocupación (evitando división por cero)
    if total_viviendas > 0:
        porcentaje_ocupacion = viviendas_ocupadas / total_viviendas * 100
    else:
        porcentaje_ocupacion = 0
    
    # Estadísticas de residentes
    if edificio_id:
        residentes = Residente.objects.filter(vivienda__edificio_id=edificio_id, activo=True)
    else:
        residentes = Residente.objects.filter(activo=True)
    
    total_residentes = residentes.count()
    
    # Estadísticas por tipo de residente
    tipos_residentes = TipoResidente.objects.all()
    estadisticas_tipos = []
    
    for tipo in tipos_residentes:
        if edificio_id:
            cantidad = Residente.objects.filter(tipo_residente=tipo, vivienda__edificio_id=edificio_id, activo=True).count()
        else:
            cantidad = Residente.objects.filter(tipo_residente=tipo, activo=True).count()
        
        if cantidad > 0:
            estadisticas_tipos.append({
                'nombre': tipo.nombre,
                'cantidad': cantidad,
                'es_propietario': tipo.es_propietario
            })
    
    # Estadísticas de visitas
    if edificio_id:
        visitas_activas = Visita.objects.filter(vivienda_destino__edificio_id=edificio_id, fecha_hora_salida__isnull=True).count()
        ultimas_visitas = Visita.objects.filter(vivienda_destino__edificio_id=edificio_id).order_by('-fecha_hora_entrada')[:5]
    else:
        visitas_activas = Visita.objects.filter(fecha_hora_salida__isnull=True).count()
        ultimas_visitas = Visita.objects.all().order_by('-fecha_hora_entrada')[:5]
    
    # Obtener los últimos movimientos de residentes
    if edificio_id:
        ultimos_movimientos = MovimientoResidente.objects.filter(
            Q(residente__vivienda__edificio_id=edificio_id)
        ).order_by('-fecha_hora_entrada', '-fecha_hora_salida')[:5]
    else:
        ultimos_movimientos = MovimientoResidente.objects.all().order_by('-fecha_hora_entrada', '-fecha_hora_salida')[:5]
    
    context = {
        'edificios': edificios,
        'edificio_seleccionado': edificio_seleccionado,
        'edificio_nombre': edificio_nombre,
        'total_viviendas': total_viviendas,
        'viviendas_ocupadas': viviendas_ocupadas,
        'viviendas_desocupadas': viviendas_desocupadas,
        'viviendas_mantenimiento': viviendas_mantenimiento,
        'porcentaje_ocupacion': porcentaje_ocupacion,
        'total_residentes': total_residentes,
        'estadisticas_tipos': estadisticas_tipos,
        'visitas_activas': visitas_activas,
        'ultimas_visitas': ultimas_visitas,
        'ultimos_movimientos': ultimos_movimientos,
    }
    
    return render(request, 'dashboard.html', context)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

@login_required
def perfil(request):
    return render(request, 'perfil.html', {'usuario': request.user})

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)