from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Count
from viviendas.models import Edificio, Vivienda, Residente
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
    else:
        viviendas = Vivienda.objects.all()
        edificio_seleccionado = None
    
    total_viviendas = viviendas.count()
    viviendas_ocupadas = viviendas.filter(estado='OCUPADO').count()
    viviendas_desocupadas = viviendas.filter(estado='DESOCUPADO').count()
    viviendas_mantenimiento = viviendas.filter(estado='MANTENIMIENTO').count()
    
    total_residentes = Residente.objects.count()
    visitas_activas = Visita.objects.filter(fecha_hora_salida__isnull=True).count()
    
    # Obtener las últimas visitas
    ultimas_visitas = Visita.objects.all().order_by('-fecha_hora_entrada')[:5]
    
    # Obtener los últimos movimientos de residentes
    ultimos_movimientos = MovimientoResidente.objects.all().order_by('-fecha_hora_entrada', '-fecha_hora_salida')[:5]
    
    context = {
        'edificios': edificios,
        'edificio_seleccionado': edificio_seleccionado,
        'total_viviendas': total_viviendas,
        'viviendas_ocupadas': viviendas_ocupadas,
        'viviendas_desocupadas': viviendas_desocupadas,
        'viviendas_mantenimiento': viviendas_mantenimiento,
        'porcentaje_ocupacion': (viviendas_ocupadas / total_viviendas * 100) if total_viviendas > 0 else 0,
        'total_residentes': total_residentes,
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