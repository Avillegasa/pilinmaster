from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from .models import Usuario, Rol
from .forms import UsuarioCreationForm, UsuarioChangeForm, RolForm
from django.core.exceptions import PermissionDenied

# Función auxiliar para comprobar si es administrador
def es_admin(user):
    return (user.is_authenticated and 
            hasattr(user, 'rol') and 
            user.rol is not None and 
            user.rol.nombre in ['Administrador', 'Gerente'])

# Función auxiliar para verificar si un usuario es administrador
def es_usuario_administrador(usuario):
    return (hasattr(usuario, 'rol') and 
            usuario.rol is not None and 
            usuario.rol.nombre == 'Administrador')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return es_admin(self.request.user)

# Vistas de Usuarios
class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        queryset = Usuario.objects.select_related('rol').all()
        
        # ✅ FILTROS MEJORADOS
        buscar = self.request.GET.get('buscar', '').strip()
        rol_id = self.request.GET.get('rol', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        
        # Filtro por búsqueda
        if buscar:
            queryset = queryset.filter(
                Q(first_name__icontains=buscar) |
                Q(last_name__icontains=buscar) |
                Q(username__icontains=buscar) |
                Q(email__icontains=buscar) |
                Q(numero_documento__icontains=buscar)
            )
        
        # Filtro por rol
        if rol_id:
            try:
                rol_id = int(rol_id)
                queryset = queryset.filter(rol_id=rol_id)
            except (ValueError, TypeError):
                pass
        
        # Filtro por estado
        if estado == 'activo':
            queryset = queryset.filter(is_active=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ✅ AGREGAR ROLES AL CONTEXTO
        context['roles'] = Rol.objects.all().order_by('nombre')
        # ✅ MANTENER VALORES DE FILTROS
        context['filtros'] = {
            'buscar': self.request.GET.get('buscar', ''),
            'rol': self.request.GET.get('rol', ''),
            'estado': self.request.GET.get('estado', ''),
        }
        return context

class UsuarioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

# Vista personalizada para cambio de estado con protección de administradores
class UsuarioChangeStateView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # ✅ PROTECCIÓN CRÍTICA: No permitir cambio de estado a administradores
        if es_usuario_administrador(usuario):
            messages.error(request, "❌ No se puede cambiar el estado de un usuario Administrador por razones de seguridad.")
            return HttpResponseRedirect(reverse_lazy('usuario-list'))
        
        return render(request, 'usuarios/usuario_change_state.html', {'usuario': usuario})
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # ✅ PROTECCIÓN CRÍTICA: Verificar que no sea administrador
        if es_usuario_administrador(usuario):
            messages.error(request, "❌ OPERACIÓN DENEGADA: No se puede modificar el estado de un usuario Administrador.")
            return HttpResponseRedirect(reverse_lazy('usuario-list'))
        
        # ✅ PROTECCIÓN ADICIONAL: Verificar si es el mismo usuario
        if usuario == request.user:
            messages.error(request, "❌ No puedes cambiar tu propio estado.")
            return HttpResponseRedirect(reverse_lazy('usuario-list'))
        
        # ✅ PROTECCIÓN ADICIONAL: Verificar que quede al menos un administrador activo
        if es_usuario_administrador(request.user) and usuario.is_active:
            # Contar administradores activos
            admins_activos = Usuario.objects.filter(
                rol__nombre='Administrador', 
                is_active=True
            ).exclude(pk=usuario.pk).count()
            
            if admins_activos == 0:
                messages.error(request, "❌ No se puede desactivar este usuario porque debe quedar al menos un Administrador activo en el sistema.")
                return HttpResponseRedirect(reverse_lazy('usuario-list'))
        
        # Proceder con el cambio de estado
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = "activado" if usuario.is_active else "desactivado"
        messages.success(request, f'✅ El usuario {usuario.username} ha sido {estado} correctamente.')
        return HttpResponseRedirect(reverse_lazy('usuario-list'))

class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'usuarios/usuario_detail.html'
    context_object_name = 'usuario'

# Vistas de Roles con protección adicional
class RolListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Rol
    template_name = 'usuarios/rol_list.html'
    context_object_name = 'roles'

class RolCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Rol
    form_class = RolForm
    template_name = 'usuarios/rol_form.html'
    success_url = reverse_lazy('rol-list')

class RolUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Rol
    form_class = RolForm
    template_name = 'usuarios/rol_form.html'
    success_url = reverse_lazy('rol-list')

class RolDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Rol
    template_name = 'usuarios/rol_confirm_delete.html'
    success_url = reverse_lazy('rol-list')
    
    def dispatch(self, request, *args, **kwargs):
        rol = self.get_object()
        
        # ✅ PROTECCIÓN CRÍTICA: No permitir eliminar el rol "Administrador"
        if rol.nombre == 'Administrador':
            messages.error(request, "❌ OPERACIÓN DENEGADA: No se puede eliminar el rol 'Administrador' por razones de seguridad del sistema.")
            return HttpResponseRedirect(reverse_lazy('rol-list'))
        
        # ✅ PROTECCIÓN ADICIONAL: Verificar si hay usuarios asignados a este rol
        if rol.usuarios.exists():
            messages.error(request, f"❌ No se puede eliminar el rol '{rol.nombre}' porque hay usuarios asignados a este rol.")
            return HttpResponseRedirect(reverse_lazy('rol-list'))
        
        return super().dispatch(request, *args, **kwargs)

# ✅ NUEVA VISTA: API para verificar si un usuario puede ser modificado
@login_required
def verificar_usuario_modificable(request, pk):
    """
    API endpoint para verificar si un usuario puede ser modificado
    Usado por JavaScript para validaciones del lado cliente
    """
    if not es_admin(request.user):
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        usuario = Usuario.objects.get(pk=pk)
        es_administrador = es_usuario_administrador(usuario)
        es_mismo_usuario = usuario == request.user
        
        return JsonResponse({
            'modificable': not es_administrador and not es_mismo_usuario,
            'es_administrador': es_administrador,
            'es_mismo_usuario': es_mismo_usuario,
            'mensaje': get_mensaje_proteccion(usuario, request.user)
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

def get_mensaje_proteccion(usuario, usuario_actual):
    """Retorna el mensaje de protección apropiado"""
    if es_usuario_administrador(usuario):
        return "Este usuario tiene rol de Administrador y no puede ser modificado por razones de seguridad."
    elif usuario == usuario_actual:
        return "No puedes modificar tu propio estado."
    else:
        return "Usuario modificable."