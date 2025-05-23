from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Usuario, Rol
from .forms import UsuarioCreationForm, UsuarioChangeForm, RolForm
from django.contrib.auth.views import LoginView
# Función auxiliar para comprobar si es administrador
def tiene_acceso_web(user):
    return (
        user.is_authenticated and
        hasattr(user, 'rol') and
        user.rol is not None and
        user.rol.nombre in ['Administrador', 'Gerente']
    )


class AccesoWebPermitidoMixin(UserPassesTestMixin):
    def test_func(self):
        return tiene_acceso_web(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Debe ingresar desde la aplicación móvil.")
        return redirect('login')  # Puedes redirigir a otra vista si lo deseas


# Vistas de Usuarios
class UsuarioListView(LoginRequiredMixin, AccesoWebPermitidoMixin, ListView):
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

class UsuarioCreateView(LoginRequiredMixin, AccesoWebPermitidoMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

    def form_valid(self, form):
        usuario = form.save(commit=False)
        usuario.is_active = True  # Bloquea el acceso hasta confirmar
        usuario.save()
        messages.success(self.request, "Usuario creado. Podrá activar su cuenta al intentar iniciar sesión desde la app móvil.")
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()
        if user.rol is None or user.rol.nombre not in ['Administrador', 'Gerente']:
            messages.add_message(
            self.request, messages.ERROR,
            "Debe ingresar desde la aplicación móvil.",
            extra_tags='danger'
            )
            return redirect(reverse_lazy('login'))
        return super().form_valid(form)

class UsuarioUpdateView(LoginRequiredMixin, AccesoWebPermitidoMixin, UpdateView):
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

# Reemplazo de la vista DeleteView por una vista personalizada para cambiar estado
class UsuarioChangeStateView(LoginRequiredMixin, AccesoWebPermitidoMixin, View):
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        return render(request, 'usuarios/usuario_change_state.html', {'usuario': usuario})
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Verificar si es el mismo usuario que está intentando desactivarse
        if usuario == request.user:
            messages.error(request, "No puedes cambiar tu propio estado.")
            return HttpResponseRedirect(reverse_lazy('usuario-list'))
        
        # Cambiar el estado del usuario (activar/desactivar)
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = "activado" if usuario.is_active else "desactivado"
        messages.success(request, f'El usuario {usuario.username} ha sido {estado} correctamente.')
        return HttpResponseRedirect(reverse_lazy('usuario-list'))

class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'usuarios/usuario_detail.html'
    context_object_name = 'usuario'

# Vistas de Roles
class RolListView(LoginRequiredMixin, AccesoWebPermitidoMixin, ListView):
    model = Rol
    template_name = 'usuarios/rol_list.html'
    context_object_name = 'roles'

class RolCreateView(LoginRequiredMixin, AccesoWebPermitidoMixin, CreateView):
    model = Rol
    form_class = RolForm
    template_name = 'usuarios/rol_form.html'
    success_url = reverse_lazy('rol-list')

class RolUpdateView(LoginRequiredMixin, AccesoWebPermitidoMixin, UpdateView):
    model = Rol
    form_class = RolForm
    template_name = 'usuarios/rol_form.html'
    success_url = reverse_lazy('rol-list')

class RolDeleteView(LoginRequiredMixin, AccesoWebPermitidoMixin, DeleteView):
    model = Rol
    template_name = 'usuarios/rol_confirm_delete.html'
    success_url = reverse_lazy('rol-list')


