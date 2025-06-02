document.addEventListener('DOMContentLoaded', function() {
    // ✅ CORRECCIÓN: Variables con verificación de existencia
    const edificioSelect = document.getElementById('id_edificio');
    const viviendaSelect = document.getElementById('id_vivienda');
    const empleadoSelect = document.getElementById('id_empleado');
    const tipoSelect = document.getElementById('id_tipo');
    const estadoSelect = document.getElementById('id_estado');
    const fechaDesdeInput = document.getElementById('id_fecha_desde');
    const fechaHastaInput = document.getElementById('id_fecha_hasta');
    const filtroForm = document.getElementById('filtroForm');
    
    // ✅ CORRECCIÓN: Función mejorada para actualizar viviendas
    function actualizarViviendas() {
        if (!edificioSelect || !viviendaSelect) {
            console.warn('Elementos de edificio o vivienda no encontrados');
            return;
        }
        
        const edificioId = edificioSelect.value;
        const viviendaSeleccionada = viviendaSelect.value;
        
        // Limpiar viviendas actuales
        viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
        
        if (!edificioId) {
            viviendaSelect.disabled = false;
            return;
        }
        
        // Mostrar indicador de carga
        viviendaSelect.disabled = true;
        viviendaSelect.innerHTML = '<option value="">Cargando viviendas...</option>';
        
        // ✅ CORRECCIÓN: URL de API corregida y unificada
        const apiUrl = '/personal/api/viviendas-por-edificio/?edificio_id=' + edificioId;
        
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error de red: ${response.status} - ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Habilitar el select
                viviendaSelect.disabled = false;
                
                // Limpiar las opciones actuales
                viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
                
                if (Array.isArray(data) && data.length > 0) {
                    // Añadir las nuevas viviendas
                    data.forEach(vivienda => {
                        const option = document.createElement('option');
                        option.value = vivienda.id;
                        option.textContent = `${vivienda.numero} (Piso ${vivienda.piso})`;
                        viviendaSelect.appendChild(option);
                    });
                    
                    // Intentar restaurar la vivienda seleccionada previamente
                    if (viviendaSeleccionada) {
                        viviendaSelect.value = viviendaSeleccionada;
                    }
                } else {
                    // No hay viviendas disponibles
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No hay viviendas en este edificio';
                    option.disabled = true;
                    viviendaSelect.appendChild(option);
                }
            })
            .catch(error => {
                console.error('Error al cargar viviendas:', error);
                
                // Habilitar el select y mostrar error
                viviendaSelect.disabled = false;
                viviendaSelect.innerHTML = '<option value="">Error al cargar viviendas</option>';
                
                // ✅ CORRECCIÓN: Mostrar notificación de error al usuario
                mostrarNotificacionError('No se pudieron cargar las viviendas del edificio seleccionado.');
            });
    }
    
    // ✅ CORRECCIÓN: Función para mostrar notificaciones de error
    function mostrarNotificacionError(mensaje) {
        // Remover notificaciones anteriores
        const existingAlert = document.querySelector('.alert.alert-warning.auto-dismiss');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // Crear nueva notificación
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-warning alert-dismissible fade show auto-dismiss';
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.style.maxWidth = '400px';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Advertencia:</strong> ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // ✅ CORRECCIÓN: Validación mejorada de fechas
    function validarFechas() {
        if (!fechaDesdeInput || !fechaHastaInput) return true;
        
        const fechaDesde = fechaDesdeInput.value ? new Date(fechaDesdeInput.value) : null;
        const fechaHasta = fechaHastaInput.value ? new Date(fechaHastaInput.value) : null;
        
        // Limpiar estados de validación anteriores
        fechaDesdeInput.classList.remove('is-invalid');
        fechaHastaInput.classList.remove('is-invalid');
        
        if (fechaDesde && fechaHasta && fechaDesde > fechaHasta) {
            fechaDesdeInput.classList.add('is-invalid');
            fechaHastaInput.classList.add('is-invalid');
            
            mostrarNotificacionError('La fecha desde no puede ser posterior a la fecha hasta.');
            return false;
        }
        
        // Validar que las fechas no sean muy lejanas en el futuro
        const hoy = new Date();
        const maxFecha = new Date();
        maxFecha.setFullYear(hoy.getFullYear() + 2); // Máximo 2 años en el futuro
        
        if (fechaDesde && fechaDesde > maxFecha) {
            fechaDesdeInput.classList.add('is-invalid');
            mostrarNotificacionError('La fecha desde no puede ser más de 2 años en el futuro.');
            return false;
        }
        
        if (fechaHasta && fechaHasta > maxFecha) {
            fechaHastaInput.classList.add('is-invalid');
            mostrarNotificacionError('La fecha hasta no puede ser más de 2 años en el futuro.');
            return false;
        }
        
        return true;
    }
    
    // ✅ CORRECCIÓN: Event listeners con debounce para mejor rendimiento
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Actualizar viviendas con debounce
    const debouncedActualizarViviendas = debounce(actualizarViviendas, 300);
    
    // ✅ CORRECCIÓN: Event listeners mejorados con verificación
    if (edificioSelect) {
        edificioSelect.addEventListener('change', function() {
            debouncedActualizarViviendas();
            
            // Auto-submit si está configurado
            if (this.dataset.autosubmit === "true" && filtroForm) {
                setTimeout(() => filtroForm.submit(), 500);
            }
        });
    }
    
    if (viviendaSelect) {
        viviendaSelect.addEventListener('change', function() {
            if (this.dataset.autosubmit !== "false" && filtroForm) {
                filtroForm.submit();
            }
        });
    }
    
    if (empleadoSelect) {
        empleadoSelect.addEventListener('change', function() {
            if (this.dataset.autosubmit !== "false" && filtroForm) {
                filtroForm.submit();
            }
        });
    }
    
    if (tipoSelect) {
        tipoSelect.addEventListener('change', function() {
            if (this.dataset.autosubmit !== "false" && filtroForm) {
                filtroForm.submit();
            }
        });
    }
    
    if (estadoSelect) {
        estadoSelect.addEventListener('change', function() {
            if (this.dataset.autosubmit !== "false" && filtroForm) {
                filtroForm.submit();
            }
        });
    }
    
    // ✅ CORRECCIÓN: Validación de fechas con feedback visual
    if (fechaDesdeInput) {
        fechaDesdeInput.addEventListener('change', function() {
            validarFechas();
        });
    }
    
    if (fechaHastaInput) {
        fechaHastaInput.addEventListener('change', function() {
            validarFechas();
        });
    }
    
    // ✅ CORRECCIÓN: Validación del formulario antes de enviar
    if (filtroForm) {
        filtroForm.addEventListener('submit', function(e) {
            if (!validarFechas()) {
                e.preventDefault();
                return false;
            }
            
            // Mostrar indicador de carga
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Filtrando...';
                
                // Restaurar después de 3 segundos como fallback
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 3000);
            }
        });
    }
    
    // ✅ CORRECCIÓN: Inicializar viviendas si hay un edificio seleccionado
    if (edificioSelect && edificioSelect.value) {
        actualizarViviendas();
    }
    
    // ✅ CORRECCIÓN: Funcionalidad de reseteo mejorada
    const resetButton = document.querySelector('a[href*="asignacion-list"]:not([href*="?"]), .btn-clear');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            // Si es un enlace de reset, confirmar
            if (this.href && this.href.includes('asignacion-list') && !this.href.includes('?')) {
                const hasFilters = edificioSelect?.value || 
                                 viviendaSelect?.value || 
                                 empleadoSelect?.value || 
                                 tipoSelect?.value || 
                                 estadoSelect?.value || 
                                 fechaDesdeInput?.value || 
                                 fechaHastaInput?.value;
                
                if (hasFilters) {
                    const confirmReset = confirm('¿Estás seguro de que quieres limpiar todos los filtros?');
                    if (!confirmReset) {
                        e.preventDefault();
                        return false;
                    }
                }
            }
        });
    }
    
    // ✅ CORRECCIÓN: Funcionalidad de guardado de filtros en localStorage
    function guardarEstadoFiltros() {
        if (!localStorage) return;
        
        const filtros = {
            edificio: edificioSelect?.value || '',
            vivienda: viviendaSelect?.value || '',
            empleado: empleadoSelect?.value || '',
            tipo: tipoSelect?.value || '',
            estado: estadoSelect?.value || '',
            fecha_desde: fechaDesdeInput?.value || '',
            fecha_hasta: fechaHastaInput?.value || ''
        };
        
        localStorage.setItem('asignacion_filters', JSON.stringify(filtros));
    }
    
    function restaurarEstadoFiltros() {
        if (!localStorage) return;
        
        try {
            const filtrosGuardados = localStorage.getItem('asignacion_filters');
            if (filtrosGuardados) {
                const filtros = JSON.parse(filtrosGuardados);
                
                // Solo restaurar si los campos están vacíos (primera carga)
                const tieneValores = edificioSelect?.value || 
                                   viviendaSelect?.value || 
                                   empleadoSelect?.value || 
                                   tipoSelect?.value || 
                                   estadoSelect?.value || 
                                   fechaDesdeInput?.value || 
                                   fechaHastaInput?.value;
                
                if (!tieneValores) {
                    if (edificioSelect && filtros.edificio) edificioSelect.value = filtros.edificio;
                    if (empleadoSelect && filtros.empleado) empleadoSelect.value = filtros.empleado;
                    if (tipoSelect && filtros.tipo) tipoSelect.value = filtros.tipo;
                    if (estadoSelect && filtros.estado) estadoSelect.value = filtros.estado;
                    if (fechaDesdeInput && filtros.fecha_desde) fechaDesdeInput.value = filtros.fecha_desde;
                    if (fechaHastaInput && filtros.fecha_hasta) fechaHastaInput.value = filtros.fecha_hasta;
                    
                    // Actualizar viviendas si hay edificio seleccionado
                    if (edificioSelect && edificioSelect.value) {
                        setTimeout(() => {
                            actualizarViviendas();
                            if (viviendaSelect && filtros.vivienda) {
                                setTimeout(() => {
                                    viviendaSelect.value = filtros.vivienda;
                                }, 500);
                            }
                        }, 100);
                    }
                }
            }
        } catch (error) {
            console.warn('Error al restaurar filtros:', error);
        }
    }
    
    // Guardar estado al cambiar filtros
    [edificioSelect, viviendaSelect, empleadoSelect, tipoSelect, estadoSelect, fechaDesdeInput, fechaHastaInput]
        .filter(Boolean)
        .forEach(element => {
            element.addEventListener('change', guardarEstadoFiltros);
        });
    
    // Restaurar filtros al cargar (solo si no hay valores en URL)
    if (!window.location.search) {
        restaurarEstadoFiltros();
    }
    
    console.log('✅ Filtros de asignaciones inicializados correctamente');
});