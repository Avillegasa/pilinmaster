from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol
from .forms import UsuarioCreationForm, UsuarioEditForm

class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioEditForm
    model = Usuario

    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')

    # ✅ Mostrar nueva_password en lugar de password edit
    fieldsets = (
        (None, {'fields': ('username', 'nueva_password')}),  # <- Aquí cambia "password" por "nueva_password"
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'telefono', 'numero_documento', 'foto')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Asignaciones', {'fields': ('rol',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'rol', 'is_staff', 'is_active'
            )
        }),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Rol, RolAdmin)
