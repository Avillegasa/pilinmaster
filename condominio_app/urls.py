from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    
    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), 
         name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), 
         name='password_change_done'),

    # Agregar estas URLs para el restablecimiento de contraseña
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    
    # Incluir URLs de las aplicaciones
    path('usuarios/', include('usuarios.urls')),
    path('viviendas/', include('viviendas.urls')),
    path('accesos/', include('accesos.urls')),
    path('personal/', include('personal.urls')),  # Nueva aplicación de personal
    path('financiero/', include('financiero.urls')),  # Nueva aplicación de gestión financiera
    
    # OAuth URLs para autenticación con Gmail (implementación futura)
    path('accounts/', include('allauth.urls')),
    
    # API endpoints
    path('api/visitas/historial/', include('accesos.urls')),
    path('api/viviendas/<int:vivienda_id>/residentes/', include('accesos.urls')),
]

# Servir archivos estáticos y media en modo de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manejadores de errores
handler404 = 'condominio_app.views.handler404'
handler500 = 'condominio_app.views.handler500'