# viviendas/urls.py

from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Vistas principales
    path('', views.ViviendaListView.as_view(), name='vivienda-list'),
    path('crear/', views.ViviendaCreateView.as_view(), name='vivienda-create'),
    path('<int:pk>/', views.ViviendaDetailView.as_view(), name='vivienda-detail'),
    path('<int:pk>/editar/', views.ViviendaUpdateView.as_view(), name='vivienda-update'),
    path('<int:pk>/eliminar/', views.ViviendaDeleteView.as_view(), name='vivienda-delete'),
    path('<int:pk>/baja/', views.ViviendaBajaView.as_view(), name='vivienda-baja'),
    
    # Vistas de edificios
    path('edificios/', views.EdificioListView.as_view(), name='edificio-list'),
    path('edificios/crear/', views.EdificioCreateView.as_view(), name='edificio-create'),
    path('edificios/<int:pk>/', views.EdificioDetailView.as_view(), name='edificio-detail'),
    path('edificios/<int:pk>/editar/', views.EdificioUpdateView.as_view(), name='edificio-update'),
    path('edificios/<int:pk>/eliminar/', views.EdificioDeleteView.as_view(), name='edificio-delete'),
    
    # Vistas de residentes
    path('residentes/', views.ResidenteListView.as_view(), name='residente-list'),
    path('residentes/crear/', views.ResidenteCreateView.as_view(), name='residente-create'),
    path('residentes/<int:pk>/', views.ResidenteDetailView.as_view(), name='residente-detail'),
    path('residentes/<int:pk>/editar/', views.ResidenteUpdateView.as_view(), name='residente-update'),
    # ✅ LÍNEA ELIMINADA - No existe ResidenteDeleteView, se usa cambio de estado en usuarios
    
    # API endpoints
    path('api/edificio/<int:edificio_id>/viviendas/', api.viviendas_por_edificio, name='api-viviendas-por-edificio'),
    path('api/edificio/<int:edificio_id>/pisos/', api.pisos_por_edificio, name='api-pisos-por-edificio'),
    path('api/vivienda/<int:vivienda_id>/residentes/', api.residentes_por_vivienda, name='api-residentes-por-vivienda'),
]