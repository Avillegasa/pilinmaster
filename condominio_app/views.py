from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Count
from viviendas.models import Vivienda, Residente
from accesos.models import Visita, MovimientoResidente

@login_required
def dashboard(request):
    # Estadísticas para el dashboard
    total_viviendas = Vivienda.objects.count()
    viviendas_ocupadas = Vivienda.objects.filter(estado='OCUPADO').count()
    total_residentes = Residente.objects.count()
    visitas_activas = Visita.objects.filter(fecha_hora_salida__isnull=True).count()
    
    # Obtener las últimas visitas
    ultimas_visitas = Visita.objects.all().order_by('-fecha_hora_entrada')[:5]
    
    # Obtener los últimos movimientos de residentes
    ultimos_movimientos = MovimientoResidente.objects.all().order_by('-fecha_hora_entrada', '-fecha_hora_salida')[:5]
    
    context = {
        'total_viviendas': total_viviendas,
        'viviendas_ocupadas': viviendas_ocupadas,
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