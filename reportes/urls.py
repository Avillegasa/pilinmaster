from django.urls import path
from . import views

urlpatterns = [
    # Listado y gestión de configuraciones de reportes
    path('', views.ReporteListView.as_view(), name='reporte-list'),
    path('nuevo/', views.ReporteCreateView.as_view(), name='reporte-create'),
    path('<int:pk>/editar/', views.ReporteUpdateView.as_view(), name='reporte-update'),
    path('<int:pk>/eliminar/', views.ReporteDeleteView.as_view(), name='reporte-delete'),
    
    # Vistas para visualización y exportación
    path('<int:pk>/vista-previa/', views.reporte_preview, name='reporte-preview'),
    
    # Acciones sobre reportes
    path('<int:pk>/favorito/', views.reporte_toggle_favorito, name='reporte-toggle-favorito'),
    path('<int:pk>/duplicar/', views.reporte_duplicar, name='reporte-duplicar'),
]