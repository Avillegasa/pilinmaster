from django.urls import path
from . import views
from .views_api import CustomTokenObtainPairView,usuario_actual
from .views import AlertaListView  # si está en el mismo archivo
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    # URLs para Usuario
    path('', views.UsuarioListView.as_view(), name='usuario-list'),
    path('nuevo/', views.UsuarioCreateView.as_view(), name='usuario-create'),
    path('<int:pk>/', views.UsuarioDetailView.as_view(), name='usuario-detail'),
    path('<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario-update'),
    path('<int:pk>/estado/', views.UsuarioChangeStateView.as_view(), name='usuario-change-state'),
    
    # URLs para Rol
    path('roles/', views.RolListView.as_view(), name='rol-list'),
    path('roles/nuevo/', views.RolCreateView.as_view(), name='rol-create'),
    path('roles/<int:pk>/editar/', views.RolUpdateView.as_view(), name='rol-update'),
    path('roles/<int:pk>/eliminar/', views.RolDeleteView.as_view(), name='rol-delete'),

    # carga de viviendas url
    path('ajax/cargar-viviendas/', views.cargar_viviendas, name='ajax-cargar-viviendas'),
    #URLs para movil usuario
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', usuario_actual, name='usuario_actual'),
    
    path('verificar-email/<uidb64>/<token>/', views.VerificarEmailView.as_view(), name='verificar-email'),

]