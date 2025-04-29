from django.urls import path
from . import views

urlpatterns = [
    # URLs para Edificio
    path('edificios/', views.EdificioListView.as_view(), name='edificio-list'),
    path('edificios/nuevo/', views.EdificioCreateView.as_view(), name='edificio-create'),
    path('edificios/<int:pk>/', views.EdificioDetailView.as_view(), name='edificio-detail'),
    path('edificios/<int:pk>/editar/', views.EdificioUpdateView.as_view(), name='edificio-update'),
    path('edificios/<int:pk>/eliminar/', views.EdificioDeleteView.as_view(), name='edificio-delete'),
    
    # URLs para Vivienda
    path('', views.ViviendaListView.as_view(), name='vivienda-list'),
    path('nueva/', views.ViviendaCreateView.as_view(), name='vivienda-create'),
    path('<int:pk>/', views.ViviendaDetailView.as_view(), name='vivienda-detail'),
    path('<int:pk>/editar/', views.ViviendaUpdateView.as_view(), name='vivienda-update'),
    path('<int:pk>/eliminar/', views.ViviendaDeleteView.as_view(), name='vivienda-delete'),
    
    # URLs para Residente
    path('residentes/', views.ResidenteListView.as_view(), name='residente-list'),
    path('residentes/nuevo/', views.ResidenteCreateView.as_view(), name='residente-create'),
    path('residentes/<int:pk>/', views.ResidenteDetailView.as_view(), name='residente-detail'),
    path('residentes/<int:pk>/editar/', views.ResidenteUpdateView.as_view(), name='residente-update'),
    path('residentes/<int:pk>/eliminar/', views.ResidenteDeleteView.as_view(), name='residente-delete'),
    
    # URLs para TipoResidente
    path('tipos-residentes/', views.TipoResidenteListView.as_view(), name='tipo-residente-list'),
    path('tipos-residentes/nuevo/', views.TipoResidenteCreateView.as_view(), name='tipo-residente-create'),
    path('tipos-residentes/<int:pk>/editar/', views.TipoResidenteUpdateView.as_view(), name='tipo-residente-update'),
    path('tipos-residentes/<int:pk>/eliminar/', views.TipoResidenteDeleteView.as_view(), name='tipo-residente-delete'),
]