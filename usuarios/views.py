from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Usuario, Rol
from .forms import UsuarioCreationForm, UsuarioChangeForm, RolForm

# Función auxiliar para comprobar si es administrador
def es_admin(user):
    return user.is_authenticated and user.rol and user.rol.nombre == 'Administrador'

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return es_admin(self.request.user)

# Vistas de Usuarios
class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

class UsuarioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
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

 
class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

# Reemplazo de la vista DeleteView por una vista personalizada para cambiar estado
class UsuarioChangeStateView(LoginRequiredMixin, AdminRequiredMixin, View):
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


