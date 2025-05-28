document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Inicializando filtros de residentes...');
    
    // Elementos DOM
    const edificioSelect = document.getElementById('edificio');
    const viviendaSelect = document.getElementById('vivienda');
    const tipoSelect = document.getElementById('tipo_residente');
    const estadoSelect = document.getElementById('estado');
    const filtroForm = document.getElementById('filtroForm');
    const buscarInput = document.getElementById('buscar');
    
    // ✅ FUNCIÓN MEJORADA: Actualizar viviendas según edificio seleccionado
    function actualizarViviendas() {
        if (!edificioSelect || !viviendaSelect) return;
        
        const edificioId = edificioSelect.value || 0;
        const viviendaSeleccionada = viviendaSelect.value; // Guardar selección actual
        
        // Mostrar indicador de carga
        viviendaSelect.disabled = true;
        viviendaSelect.innerHTML = '<option value="">Cargando viviendas...</option>';
        
        // URL de la API
        const apiUrl = `/viviendas/api/edificio/${edificioId}/viviendas/`;
        
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Limpiar opciones
                viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
                
                // ✅ FILTRAR SOLO VIVIENDAS ACTIVAS
                const viviendasActivas = data.filter(vivienda => vivienda.activo);
                
                // Añadir viviendas activas
                viviendasActivas.forEach(vivienda => {
                    const option = document.createElement('option');
                    option.value = vivienda.id;
                    option.textContent = `${vivienda.edificio_nombre} - ${vivienda.numero} (Piso ${vivienda.piso})`;
                    
                    // Restaurar selección si coincide
                    if (vivienda.id == viviendaSeleccionada) {
                        option.selected = true;
                    }
                    
                    viviendaSelect.appendChild(option);
                });
                
                // Mensaje si no hay viviendas
                if (viviendasActivas.length === 0) {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No hay viviendas activas en este edificio';
                    option.disabled = true;
                    viviendaSelect.appendChild(option);
                }
                
                viviendaSelect.disabled = false;
                console.log(`✅ Cargadas ${viviendasActivas.length} viviendas para edificio ${edificioId}`);
            })
            .catch(error => {
                console.error('❌ Error al cargar viviendas:', error);
                viviendaSelect.innerHTML = '<option value="">Error al cargar viviendas</option>';
                viviendaSelect.disabled = false;
                
                // Mostrar mensaje de error al usuario
                mostrarNotificacion('Error al cargar las viviendas. Inténtalo de nuevo.', 'error');
            });
    }
    
    // ✅ FUNCIÓN: Mostrar notificaciones
    function mostrarNotificacion(mensaje, tipo = 'info') {
        // Crear elemento de notificación
        const notificacion = document.createElement('div');
        notificacion.className = `alert alert-${tipo === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
        notificacion.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notificacion.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notificacion);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.remove();
            }
        }, 5000);
    }
    
    // ✅ FUNCIÓN: Aplicar filtros automáticamente (solo para algunos campos)
    function aplicarFiltrosAutomaticos() {
        // Solo aplicar automáticamente para selects, no para búsqueda de texto
        if (filtroForm) {
            filtroForm.submit();
        }
    }
    
    // ✅ FUNCIÓN: Validar y limpiar formulario
    function validarFormulario() {
        const valores = {
            buscar: buscarInput ? buscarInput.value.trim() : '',
            edificio: edificioSelect ? edificioSelect.value : '',
            vivienda: viviendaSelect ? viviendaSelect.value : '',
            tipo: tipoSelect ? tipoSelect.value : '',
            estado: estadoSelect ? estadoSelect.value : ''
        };
        
        // Si no hay filtros activos, mostrar advertencia
        const hayFiltros = Object.values(valores).some(valor => valor !== '');
        if (!hayFiltros) {
            console.log('ℹ️ No hay filtros activos - mostrando todos los residentes');
        }
        
        return valores;
    }
    
    // ✅ EVENT LISTENERS
    
    // Cambio en edificio
    if (edificioSelect) {
        edificioSelect.addEventListener('change', function() {
            console.log(`🏢 Edificio seleccionado: ${this.value}`);
            actualizarViviendas();
            
            // NO aplicar filtros automáticamente - esperar a que el usuario termine
            // Solo limpiar vivienda seleccionada si cambió edificio
            if (viviendaSelect) {
                viviendaSelect.value = '';
            }
        });
    }
    
    // Cambio en vivienda
    if (viviendaSelect) {
        viviendaSelect.addEventListener('change', function() {
            console.log(`🏠 Vivienda seleccionada: ${this.value}`);
            // Aplicar filtros automáticamente cuando se selecciona vivienda
            aplicarFiltrosAutomaticos();
        });
    }
    
    // Cambio en tipo de residente
    if (tipoSelect) {
        tipoSelect.addEventListener('change', function() {
            console.log(`👤 Tipo seleccionado: ${this.value}`);
            aplicarFiltrosAutomaticos();
        });
    }
    
    // Cambio en estado
    if (estadoSelect) {
        estadoSelect.addEventListener('change', function() {
            console.log(`📊 Estado seleccionado: ${this.value}`);
            aplicarFiltrosAutomaticos();
        });
    }
    
    // ✅ BÚSQUEDA CON DEBOUNCE (no automática)
    if (buscarInput) {
        let timeoutBusqueda;
        
        buscarInput.addEventListener('input', function() {
            const termino = this.value.trim();
            
            // Limpiar timeout anterior
            clearTimeout(timeoutBusqueda);
            
            // Si el término está vacío o es muy corto, no buscar automáticamente
            if (termino.length < 3 && termino.length > 0) {
                return;
            }
            
            // Aplicar filtros después de 1 segundo de inactividad
            timeoutBusqueda = setTimeout(() => {
                console.log(`🔍 Buscando: "${termino}"`);
                aplicarFiltrosAutomaticos();
            }, 1000);
        });
        
        // Buscar al presionar Enter
        buscarInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(timeoutBusqueda);
                aplicarFiltrosAutomaticos();
            }
        });
    }
    
    // ✅ VALIDAR ENVÍO DE FORMULARIO
    if (filtroForm) {
        filtroForm.addEventListener('submit', function(e) {
            const valores = validarFormulario();
            console.log('📋 Enviando filtros:', valores);
            
            // Mostrar indicador de carga
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const textoOriginal = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Filtrando...';
                submitBtn.disabled = true;
                
                // Restaurar botón después de un tiempo
                setTimeout(() => {
                    submitBtn.innerHTML = textoOriginal;
                    submitBtn.disabled = false;
                }, 2000);
            }
        });
    }
    
    // ✅ INICIALIZACIÓN
    
    // Cargar viviendas si hay edificio preseleccionado
    if (edificioSelect && edificioSelect.value) {
        console.log('🔄 Cargando viviendas para edificio preseleccionado:', edificioSelect.value);
        actualizarViviendas();
    }
    
    // ✅ FUNCIONES ADICIONALES PARA MEJORAR UX
    
    // Resaltar filtros activos
    function resaltarFiltrosActivos() {
        const campos = [edificioSelect, viviendaSelect, tipoSelect, estadoSelect, buscarInput];
        
        campos.forEach(campo => {
            if (campo && campo.value) {
                campo.style.borderColor = '#0d6efd';
                campo.style.boxShadow = '0 0 5px rgba(13, 110, 253, 0.3)';
            }
        });
    }
    
    // Aplicar resaltado inicial
    resaltarFiltrosActivos();
    
    // ✅ MANEJO DE ERRORES GLOBAL PARA ESTA PÁGINA
    window.addEventListener('error', function(e) {
        console.error('❌ Error en filtros de residentes:', e.error);
    });
    
    // ✅ FUNCIÓN PARA LIMPIAR TODOS LOS FILTROS
    window.limpiarFiltrosResidentes = function() {
        if (buscarInput) buscarInput.value = '';
        if (edificioSelect) edificioSelect.value = '';
        if (viviendaSelect) {
            viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
            viviendaSelect.value = '';
        }
        if (tipoSelect) tipoSelect.value = '';
        if (estadoSelect) estadoSelect.value = '';
        
        // Enviar formulario limpio
        if (filtroForm) {
            filtroForm.submit();
        }
    };
    
    // ✅ FUNCIÓN PARA MOSTRAR ESTADÍSTICAS DE FILTROS
    window.mostrarEstadisticasFiltros = function() {
        const totalFilas = document.querySelectorAll('tbody tr').length;
        const filasVisibles = document.querySelectorAll('tbody tr:not(.d-none)').length;
        
        console.log(`📊 Estadísticas de filtros: ${filasVisibles}/${totalFilas} residentes mostrados`);
        
        if (totalFilas === 0) {
            mostrarNotificacion('No hay residentes registrados en el sistema.', 'info');
        } else if (filasVisibles === 0) {
            mostrarNotificacion('No se encontraron residentes con los filtros aplicados.', 'warning');
        }
    };
    
    console.log('✅ Filtros de residentes inicializados correctamente');
    
    // Mostrar estadísticas iniciales
    setTimeout(mostrarEstadisticasFiltros, 500);
});