from django.urls import path
from . import views
from . import api

urlpatterns = [
    # URLs para Puestos
    path('puestos/', views.PuestoListView.as_view(), name='puesto-list'),
    path('puestos/nuevo/', views.PuestoCreateView.as_view(), name='puesto-create'),
    path('puestos/<int:pk>/editar/', views.PuestoUpdateView.as_view(), name='puesto-update'),
    path('puestos/<int:pk>/eliminar/', views.PuestoDeleteView.as_view(), name='puesto-delete'),
    
    # URLs para Empleados
    path('empleados/', views.EmpleadoListView.as_view(), name='empleado-list'),
    path('empleados/nuevo/', views.EmpleadoCreateView.as_view(), name='empleado-create'),
    path('empleados/<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado-detail'),
    path('empleados/<int:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='empleado-update'),
    path('empleados/<int:pk>/estado/', views.empleado_change_state, name='empleado-change-state'),
    
    # URLs para Asignaciones
    path('asignaciones/', views.AsignacionListView.as_view(), name='asignacion-list'),
    path('asignaciones/nueva/', views.AsignacionCreateView.as_view(), name='asignacion-create'),
    path('asignaciones/<int:pk>/', views.AsignacionDetailView.as_view(), name='asignacion-detail'),
    path('asignaciones/<int:pk>/editar/', views.AsignacionUpdateView.as_view(), name='asignacion-update'),
    path('asignaciones/<int:pk>/estado/', views.cambiar_estado_asignacion, name='cambiar-estado-asignacion'),
    
    # API URLs
    path('api/viviendas-por-edificio/', views.viviendas_por_edificio_api, name='api-viviendas-por-edificio'),
    path('api/edificio/<int:edificio_id>/viviendas/', api.viviendas_por_edificio, name='api-viviendas-por-edificio-personal'),
]