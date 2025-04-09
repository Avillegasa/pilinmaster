from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReporteListView.as_view(), name='reporte-list'),
    path('nuevo/', views.ReporteCreateView.as_view(), name='reporte-create'),
    path('<int:pk>/generar/', views.generar_reporte, name='generar-reporte'),
    path('<int:pk>/descargar/', views.descargar_reporte, name='descargar-reporte'),
]