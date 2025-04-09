from django.urls import path
from . import views

urlpatterns = [
    # URLs para Usuario
    path('', views.UsuarioListView.as_view(), name='usuario-list'),
    path('nuevo/', views.UsuarioCreateView.as_view(), name='usuario-create'),
    path('<int:pk>/', views.UsuarioDetailView.as_view(), name='usuario-detail'),
    path('<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario-update'),
    path('<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='usuario-delete'),
    
    # URLs para Rol
    path('roles/', views.RolListView.as_view(), name='rol-list'),
    path('roles/nuevo/', views.RolCreateView.as_view(), name='rol-create'),
    path('roles/<int:pk>/editar/', views.RolUpdateView.as_view(), name='rol-update'),
    path('roles/<int:pk>/eliminar/', views.RolDeleteView.as_view(), name='rol-delete'),
]