# Este archivo ya no es necesario, pero si lo mantienes, debe estar vacío o ser una redirección
from django.urls import path, include

urlpatterns = [
    # Redirigir todo a las URLs principales
    path('', include('alertas.urls')),
]