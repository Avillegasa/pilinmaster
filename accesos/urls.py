from django.urls import path
from . import views
from . import api

urlpatterns = [
    # URLs para Visita
    path('visitas/', views.VisitaListView.as_view(), name='visita-list'),
    path('visitas/nueva/', views.VisitaCreateView.as_view(), name='visita-create'),
    path('visitas/<int:pk>/salida/', views.registrar_salida_visita, name='visita-salida'),
    
    # URLs para Movimiento de Residentes
    path('movimientos/', views.MovimientoResidenteListView.as_view(), name='movimiento-list'),
    path('movimientos/entrada/', views.MovimientoResidenteEntradaView.as_view(), name='movimiento-entrada'),
    path('movimientos/salida/', views.MovimientoResidenteSalidaView.as_view(), name='movimiento-salida'),
    
    # API URLs
    path('api/visitas/historial/', api.historial_visitas, name='api-visitas-historial'),
    path('api/viviendas/<int:vivienda_id>/residentes/', api.residentes_por_vivienda, name='api-residentes-vivienda'),
]