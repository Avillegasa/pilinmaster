from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Usuario, Rol
from .forms import UsuarioCreationForm, UsuarioEditForm, RolForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
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

    def get_queryset(self):
        queryset = super().get_queryset().filter(rol__isnull=False)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(username__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class UsuarioCreateView(LoginRequiredMixin, AccesoWebPermitidoMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

    def form_valid(self, form):
        usuario = form.save(commit=False)
        usuario.is_active = True  # Bloquea el acceso hasta confirmar
        usuario.save()
        messages.success(self.request, "Usuario creado. Podrá activar su cuenta al intentar iniciar sesión.")
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()

        if user.rol is None or user.rol.nombre not in ['Administrador', 'Gerente']:
            messages.warning(self.request, "Debe ingresar desde la aplicación móvil")
            return redirect('login')

        # 🚫 Solo para Gerente: bloquear si no verificó su correo
        if user.rol.nombre == 'Gerente' and not user.email_confirmado:
            self.enviar_verificacion_email(user)
            messages.warning(self.request, "Tu cuenta aún no ha sido verificada. Revisa tu correo para activarla.")
            return redirect('login')

        return super().form_valid(form)

    def enviar_verificacion_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = self.request.build_absolute_uri(reverse('verificar-email', kwargs={'uidb64': uid, 'token': token}))
        subject = 'Verificación de correo para TorreSegura'
        message = f'Hola {user.first_name},\n\nPor favor verifica tu cuenta haciendo clic en el siguiente enlace:\n\n{url}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


class VerificarEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.email_confirmado = True
            user.save()
            messages.success(request, "Correo verificado correctamente. Ahora puedes iniciar sesión.")
        else:
            messages.error(request, "El enlace de verificación no es válido o ha expirado.")
        return redirect('login')

class UsuarioUpdateView(LoginRequiredMixin, AccesoWebPermitidoMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEditForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Se modificó correctamente la información del usuario: {self.object.username}")
        return response

# Reemplazo de la vista DeleteView por una vista personalizada para cambiar estado
class UsuarioChangeStateView(LoginRequiredMixin, AccesoWebPermitidoMixin, View):
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        return render(request, 'usuarios/usuario_change_state.html', {'usuario': usuario})
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)

        if usuario == request.user:
            messages.add_message(request, messages.ERROR, "No puedes cambiar tu propio estado...", extra_tags='danger')
            return HttpResponseRedirect(reverse_lazy('usuario-list'))

        # Bloquear si el usuario tiene rol de alta seguridad
        if usuario.rol and usuario.rol.nombre in ['Administrador', 'Gerente']:
            messages.add_message(request, messages.ERROR, f"No puedes desactivar a un usuario con rol '{usuario.rol.nombre}'.", extra_tags='danger')
            return HttpResponseRedirect(reverse_lazy('usuario-list'))

        # Alternar estado activo
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


