from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from usuarios.views import AdminRequiredMixin
from .models import Edificio, Vivienda, Residente
from .forms import EdificioForm, ViviendaForm, ResidenteForm, ViviendaBajaForm, EdificioBajaForm, ViviendaAltaForm

# Vistas de Edificios
class EdificioListView(LoginRequiredMixin, ListView):
    model = Edificio
    template_name = 'viviendas/edificio_list.html'
    context_object_name = 'edificios'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Por defecto mostrar solo edificios activos
        activo = self.request.GET.get('activo', 'true')
        if activo == 'true':
            queryset = queryset.filter(activo=True)
        elif activo == 'false':
            queryset = queryset.filter(activo=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_activo'] = self.request.GET.get('activo', 'true')
        context['total_activos'] = Edificio.objects.filter(activo=True).count()
        context['total_inactivos'] = Edificio.objects.filter(activo=False).count()
        return context

class EdificioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Edificio
    form_class = EdificioForm
    template_name = 'viviendas/edificio_form.html'
    success_url = reverse_lazy('edificio-list')

class EdificioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Edificio
    form_class = EdificioForm
    template_name = 'viviendas/edificio_form.html'
    success_url = reverse_lazy('edificio-list')

class EdificioBajaView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'viviendas/edificio_baja.html'
    
    def get(self, request, pk):
        edificio = get_object_or_404(Edificio, pk=pk)
        viviendas_activas = edificio.viviendas.filter(activo=True).count()
        form = EdificioBajaForm(instance=edificio)
        
        return render(request, self.template_name, {
            'edificio': edificio,
            'form': form,
            'viviendas_activas': viviendas_activas
        })
    
    def post(self, request, pk):
        edificio = get_object_or_404(Edificio, pk=pk)
        form = EdificioBajaForm(request.POST, instance=edificio)
        viviendas_activas = edificio.viviendas.filter(activo=True).count()
        
        if viviendas_activas > 0 and not request.POST.get('confirmar_viviendas'):
            messages.error(request, "Debe confirmar que entiende las consecuencias para las viviendas.")
            return render(request, self.template_name, {
                'edificio': edificio,
                'form': form,
                'viviendas_activas': viviendas_activas
            })
        
        if form.is_valid():
            # Dar de baja el edificio
            edificio.activo = False
            edificio.fecha_baja = form.cleaned_data.get('fecha_baja') or timezone.now().date()
            edificio.motivo_baja = form.cleaned_data.get('motivo_baja')
            edificio.save()
            
            # Dar de baja todas las viviendas del edificio
            edificio.viviendas.filter(activo=True).update(
                activo=False,
                estado='BAJA',
                fecha_baja=edificio.fecha_baja,
                motivo_baja=f"Edificio dado de baja: {edificio.motivo_baja}"
            )
            
            messages.success(request, f"El edificio {edificio.nombre} ha sido dado de baja correctamente.")
            return redirect('edificio-list')
        
        return render(request, self.template_name, {
            'edificio': edificio,
            'form': form,
            'viviendas_activas': viviendas_activas
        })

# Eliminar completamente EdificioDeleteView

class EdificioDetailView(LoginRequiredMixin, DetailView):
    model = Edificio
    template_name = 'viviendas/edificio_detail.html'
    context_object_name = 'edificio'

# Vistas de Viviendas

class ViviendaListView(LoginRequiredMixin, ListView):
    model = Vivienda
    template_name = 'viviendas/vivienda_list.html'
    context_object_name = 'viviendas'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por edificio si se proporciona
        edificio_id = self.request.GET.get('edificio')
        if edificio_id:
            queryset = queryset.filter(edificio_id=edificio_id)
        
        # Filtrar por piso si se proporciona
        piso = self.request.GET.get('piso')
        if piso:
            queryset = queryset.filter(piso=piso)
            
        # Filtrar por estado si se proporciona
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por activo/inactivo si se proporciona
        activo = self.request.GET.get('activo')
        if activo:
            activo_bool = activo == 'true'
            queryset = queryset.filter(activo=activo_bool)
        else:
            # Por defecto mostrar solo viviendas activas
            queryset = queryset.filter(activo=True)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Añadir lista de edificios para el selector de filtro
        context['edificios'] = Edificio.objects.all()
        
        # Añadir los valores actuales del filtro
        context['filtro_edificio'] = self.request.GET.get('edificio', '')
        context['filtro_piso'] = self.request.GET.get('piso', '')
        context['filtro_estado'] = self.request.GET.get('estado', '')
        context['filtro_activo'] = self.request.GET.get('activo', 'true')
        
        # Añadir lista de pisos disponibles para el selector
        pisos = Vivienda.objects.values_list('piso', flat=True).distinct().order_by('piso')
        context['pisos'] = pisos
        
        # Añadir lista de estados para el selector
        context['estados'] = [estado[0] for estado in Vivienda.ESTADOS]
        
        # Contar el total de viviendas activas e inactivas
        context['total_activas'] = Vivienda.objects.filter(activo=True).count()
        context['total_inactivas'] = Vivienda.objects.filter(activo=False).count()
        
        return context

class ViviendaCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Vivienda
    form_class = ViviendaForm
    template_name = 'viviendas/vivienda_form.html'
    success_url = reverse_lazy('vivienda-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'✅ La vivienda {form.cleaned_data["numero"]} ha sido creada correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '❌ Error al crear la vivienda. Por favor, corrija los errores mostrados.')
        return super().form_invalid(form)


class ViviendaUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Vivienda
    form_class = ViviendaForm
    template_name = 'viviendas/vivienda_form.html'
    success_url = reverse_lazy('vivienda-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'✅ La vivienda {form.cleaned_data["numero"]} ha sido actualizada correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '❌ Error al actualizar la vivienda. Por favor, corrija los errores mostrados.')
        return super().form_invalid(form)

class ViviendaDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Vivienda
    template_name = 'viviendas/vivienda_confirm_delete.html'
    success_url = reverse_lazy('vivienda-list')

class ViviendaDetailView(LoginRequiredMixin, DetailView):
    model = Vivienda
    template_name = 'viviendas/vivienda_detail.html'
    context_object_name = 'vivienda'
    
    # En la vista ViviendaDetailView
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener estadísticas de residentes
        vivienda = self.get_object()
        
        # Estadísticas de propietarios e inquilinos
        propietarios = vivienda.residentes.filter(es_propietario=True)
        inquilinos = vivienda.residentes.filter(es_propietario=False)
        
        context['propietarios'] = propietarios
        context['inquilinos'] = inquilinos
        context['propietarios_count'] = propietarios.count()
        context['inquilinos_count'] = inquilinos.count()
        context['propietarios_activos_count'] = propietarios.filter(activo=True).count()
        context['propietarios_inactivos_count'] = propietarios.filter(activo=False).count()
        context['inquilinos_activos_count'] = inquilinos.filter(activo=True).count()
        context['inquilinos_inactivos_count'] = inquilinos.filter(activo=False).count()
        
        return context

# Vistas de Residentes
class ResidenteListView(LoginRequiredMixin, ListView):
    model = Residente
    template_name = 'viviendas/residente_list.html'
    context_object_name = 'residentes'
    paginate_by = 20  # ✅ AGREGADO: Paginación
    
    def get_queryset(self):
        queryset = Residente.objects.select_related(
            'usuario', 'vivienda', 'vivienda__edificio'
        ).all().order_by('-fecha_ingreso')
        
        # ✅ FILTRO POR BÚSQUEDA
        buscar = self.request.GET.get('buscar', '').strip()
        if buscar:
            queryset = queryset.filter(
                Q(usuario__first_name__icontains=buscar) |
                Q(usuario__last_name__icontains=buscar) |
                Q(usuario__username__icontains=buscar) |
                Q(usuario__email__icontains=buscar) |
                Q(vivienda__numero__icontains=buscar)
            )
        
        # ✅ FILTRO POR EDIFICIO
        edificio_id = self.request.GET.get('edificio', '').strip()
        if edificio_id:
            try:
                edificio_id = int(edificio_id)
                queryset = queryset.filter(vivienda__edificio_id=edificio_id)
            except (ValueError, TypeError):
                pass
        
        # ✅ FILTRO POR VIVIENDA
        vivienda_id = self.request.GET.get('vivienda', '').strip()
        if vivienda_id:
            try:
                vivienda_id = int(vivienda_id)
                queryset = queryset.filter(vivienda_id=vivienda_id)
            except (ValueError, TypeError):
                pass
            
        # ✅ FILTRO POR TIPO DE RESIDENTE (CORREGIDO)
        tipo_residente = self.request.GET.get('tipo_residente', '').strip()
        if tipo_residente == 'propietario':
            queryset = queryset.filter(es_propietario=True)
        elif tipo_residente == 'inquilino':
            queryset = queryset.filter(es_propietario=False)
            
        # ✅ FILTRO POR ESTADO (CORREGIDO)
        estado = self.request.GET.get('estado', '').strip()
        if estado == 'activo':
            queryset = queryset.filter(activo=True, usuario__is_active=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(
                Q(activo=False) | Q(usuario__is_active=False)
            )
        # Si no se especifica estado, mostrar todos
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ✅ EDIFICIOS PARA FILTRO
        context['edificios'] = Edificio.objects.filter(activo=True).order_by('nombre')
        
        # ✅ VIVIENDAS PARA FILTRO (dinámico por edificio)
        edificio_id = self.request.GET.get('edificio')
        if edificio_id:
            try:
                edificio_id = int(edificio_id)
                context['viviendas'] = Vivienda.objects.filter(
                    edificio_id=edificio_id, activo=True
                ).order_by('piso', 'numero')
            except (ValueError, TypeError):
                context['viviendas'] = Vivienda.objects.none()
        else:
            context['viviendas'] = Vivienda.objects.filter(activo=True).order_by(
                'edificio__nombre', 'piso', 'numero'
            )
        
        # ✅ VALORES DE FILTROS ACTUALES
        context['filtros'] = {
            'buscar': self.request.GET.get('buscar', ''),
            'edificio': self.request.GET.get('edificio', ''),
            'vivienda': self.request.GET.get('vivienda', ''),
            'tipo_residente': self.request.GET.get('tipo_residente', ''),
            'estado': self.request.GET.get('estado', ''),
        }
        
        # ✅ ESTADÍSTICAS
        context['total_residentes'] = Residente.objects.count()
        context['residentes_activos'] = Residente.objects.filter(
            activo=True, usuario__is_active=True
        ).count()
        context['residentes_inactivos'] = Residente.objects.filter(
            Q(activo=False) | Q(usuario__is_active=False)
        ).count()
        
        return context

class ResidenteCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Residente
    form_class = ResidenteForm
    template_name = 'viviendas/residente_form.html'
    success_url = reverse_lazy('residente-list')
    
    def form_valid(self, form):
        # Verificar que no hay conflictos antes de guardar
        usuario = form.cleaned_data.get('usuario')
        vivienda = form.cleaned_data.get('vivienda')
        
        if usuario and vivienda:
            messages.success(
                self.request, 
                f'✅ El residente {usuario.first_name} {usuario.last_name} ha sido asignado a la vivienda {vivienda.numero}.'
            )
        else:
            messages.success(self.request, '✅ El residente ha sido creado correctamente.')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '❌ Error al crear el residente. Por favor, corrija los errores mostrados.')
        return super().form_invalid(form)

class ResidenteUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Residente
    form_class = ResidenteForm
    template_name = 'viviendas/residente_form.html'
    success_url = reverse_lazy('residente-list')
    
    def form_valid(self, form):
        usuario = form.cleaned_data.get('usuario')
        vivienda = form.cleaned_data.get('vivienda')
        
        if usuario and vivienda:
            messages.success(
                self.request, 
                f'✅ Los datos del residente {usuario.first_name} {usuario.last_name} han sido actualizados.'
            )
        else:
            messages.success(self.request, '✅ El residente ha sido actualizado correctamente.')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '❌ Error al actualizar el residente. Por favor, corrija los errores mostrados.')
        return super().form_invalid(form)

class ResidenteDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Residente
    template_name = 'viviendas/residente_confirm_delete.html'
    success_url = reverse_lazy('residente-list')

class ResidenteDetailView(LoginRequiredMixin, DetailView):
    model = Residente
    template_name = 'viviendas/residente_detail.html'
    context_object_name = 'residente'

class ViviendaBajaView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    Vista para dar de baja una vivienda en lugar de eliminarla.
    Esta vista permite establecer un motivo de baja y la fecha.
    """
    template_name = 'viviendas/vivienda_baja.html'
    
    def get(self, request, pk):
        vivienda = get_object_or_404(Vivienda, pk=pk)
        
        # Verificar si tiene residentes activos
        residentes_activos = vivienda.residentes.filter(activo=True).count()
        
        form = ViviendaBajaForm(instance=vivienda)
        
        return render(request, self.template_name, {
            'vivienda': vivienda,
            'form': form,
            'residentes_activos': residentes_activos
        })
    
    def post(self, request, pk):
        vivienda = get_object_or_404(Vivienda, pk=pk)
        form = ViviendaBajaForm(request.POST, instance=vivienda)
        
        # Verificar si tiene residentes activos
        residentes_activos = vivienda.residentes.filter(activo=True).count()
        
        if residentes_activos > 0 and not request.POST.get('confirmar_residentes'):
            messages.error(request, "No se puede dar de baja una vivienda con residentes activos. Debe reubicarlos primero.")
            return render(request, self.template_name, {
                'vivienda': vivienda,
                'form': form,
                'residentes_activos': residentes_activos
            })
        
        if form.is_valid():
            # Marcar como inactiva y cambiar estado
            vivienda.activo = False
            vivienda.estado = 'BAJA'
            vivienda.fecha_baja = form.cleaned_data.get('fecha_baja') or timezone.now().date()
            vivienda.motivo_baja = form.cleaned_data.get('motivo_baja')
            vivienda.save()
            
            messages.success(request, f"La vivienda {vivienda.numero} ha sido dada de baja correctamente.")
            return redirect('vivienda-list')
        
        return render(request, self.template_name, {
            'vivienda': vivienda,
            'form': form,
            'residentes_activos': residentes_activos
        })


class ViviendaAltaView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    Vista para dar de alta una vivienda que está dada de baja.
    Esta vista permite reactivar una vivienda y establecer un motivo.
    """
    template_name = 'viviendas/vivienda_alta.html'
    
    def get(self, request, pk):
        vivienda = get_object_or_404(Vivienda, pk=pk)
        
        # ✅ VALIDACIÓN: Solo permitir dar de alta viviendas que estén dadas de baja
        if vivienda.activo:
            messages.error(request, "Esta vivienda ya está activa. No es necesario darla de alta.")
            return redirect('vivienda-detail', pk=pk)
        
        form = ViviendaAltaForm(instance=vivienda)
        
        return render(request, self.template_name, {
            'vivienda': vivienda,
            'form': form
        })
    
    def post(self, request, pk):
        vivienda = get_object_or_404(Vivienda, pk=pk)
        
        # ✅ VALIDACIÓN: Solo permitir dar de alta viviendas que estén dadas de baja
        if vivienda.activo:
            messages.error(request, "Esta vivienda ya está activa. No es necesario darla de alta.")
            return redirect('vivienda-detail', pk=pk)
        
        form = ViviendaAltaForm(request.POST, instance=vivienda)
        
        if form.is_valid():
            # Dar de alta la vivienda
            form.save()
            
            messages.success(
                request, 
                f"✅ La vivienda {vivienda.numero} ha sido dada de alta correctamente. "
                f"Su estado ahora es 'Desocupado' y está disponible para nuevas asignaciones."
            )
            return redirect('vivienda-list')
        
        return render(request, self.template_name, {
            'vivienda': vivienda,
            'form': form
        })
    
class ResidenteReactivateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    Vista para reactivar un residente directamente
    (opcional - alternativa al cambio de estado de usuario)
    """
    
    def post(self, request, pk):
        residente = get_object_or_404(Residente, pk=pk)
        
        # Verificar que el residente esté inactivo
        if residente.activo and residente.usuario.is_active:
            messages.info(request, "El residente ya está activo.")
        else:
            # Reactivar usuario y residente
            residente.usuario.is_active = True
            residente.usuario.save()
            
            residente.activo = True
            residente.save()
            
            messages.success(request, f'✅ El residente {residente.usuario.first_name} {residente.usuario.last_name} ha sido reactivado correctamente.')
        
        return redirect('residente-list')