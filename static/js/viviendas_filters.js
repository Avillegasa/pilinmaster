document.addEventListener('DOMContentLoaded', function() {
    console.log('🏠 Cargando filtros de viviendas...');
    
    // Elementos DOM
    const edificioSelect = document.getElementById('edificio');
    const pisoSelect = document.getElementById('piso');
    const estadoSelect = document.getElementById('estado');
    const activoSelect = document.getElementById('activo');
    const filtroForm = document.getElementById('filtroForm');
    
    // ✅ CORRECCIÓN CRÍTICA: Los filtros NO se aplican automáticamente
    // Solo se aplican cuando el usuario hace clic en "Aplicar Filtros"
    
    // Función para actualizar los pisos disponibles según el edificio seleccionado
    function actualizarPisos() {
        if (!edificioSelect || !pisoSelect) {
            console.log('⚠️ No se encontraron los elementos edificio o piso');
            return;
        }
        
        const edificioId = edificioSelect.value || 0;
        const pisoSeleccionado = pisoSelect.value;
        
        console.log(`🔄 Actualizando pisos para edificio: ${edificioId}`);
        
        // Deshabilitar temporalmente el select de pisos
        pisoSelect.disabled = true;
        pisoSelect.innerHTML = '<option value="">Cargando pisos...</option>';
        
        // Hacer la petición para obtener los pisos del edificio seleccionado
        fetch(`/viviendas/api/edificio/${edificioId}/pisos/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('✅ Pisos cargados:', data);
                
                // Limpiar las opciones actuales
                pisoSelect.innerHTML = '<option value="">Todos los pisos</option>';
                
                // Añadir los nuevos pisos
                data.forEach(piso => {
                    const option = document.createElement('option');
                    option.value = piso;
                    option.textContent = `Piso ${piso}`;
                    pisoSelect.appendChild(option);
                });
                
                // Intentar restaurar el piso seleccionado previamente
                if (pisoSeleccionado && data.includes(parseInt(pisoSeleccionado))) {
                    pisoSelect.value = pisoSeleccionado;
                    console.log(`🔄 Piso restaurado: ${pisoSeleccionado}`);
                }
                
                // Habilitar el select de pisos
                pisoSelect.disabled = false;
            })
            .catch(error => {
                console.error('❌ Error al cargar pisos:', error);
                
                // Restaurar estado por defecto en caso de error
                pisoSelect.innerHTML = '<option value="">Todos los pisos</option>';
                pisoSelect.disabled = false;
                
                // Mostrar mensaje de error al usuario
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error al cargar pisos',
                        text: 'No se pudieron cargar los pisos del edificio. Por favor, recargue la página.',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#dc3545'
                    });
                } else {
                    alert('Error al cargar los pisos del edificio. Por favor, recargue la página.');
                }
            });
    }
    
    // Función para manejar la relación entre estado y activo
    function sincronizarEstadoActivo() {
        if (!estadoSelect || !activoSelect) return;
        
        // Si se selecciona BAJA, automáticamente cambiar activo a false
        if (estadoSelect.value === 'BAJA') {
            activoSelect.value = 'false';
            console.log('🔄 Estado BAJA seleccionado, cambiando a inactivo');
        }
        
        // Si se selecciona inactivo, solo permitir BAJA como estado
        if (activoSelect.value === 'false') {
            if (estadoSelect.value !== 'BAJA' && estadoSelect.value !== '') {
                estadoSelect.value = 'BAJA';
                console.log('🔄 Inactivo seleccionado, cambiando estado a BAJA');
            }
        }
    }
    
    // ✅ CORRECCIÓN CRÍTICA: Solo actualizar pisos, NO enviar formulario
    if (edificioSelect) {
        edificioSelect.addEventListener('change', function() {
            console.log(`🏢 Edificio cambiado a: ${this.value}`);
            actualizarPisos();
            // ❌ REMOVIDO: NO auto-enviar formulario
            // filtroForm.submit();
        });
        
        // Cargar las viviendas iniciales si hay un edificio preseleccionado
        if (edificioSelect.value) {
            console.log('🔄 Cargando pisos iniciales para edificio preseleccionado');
            actualizarPisos();
        }
    }
    
    // ✅ CORRECCIÓN: Solo sincronizar estados, NO enviar formulario
    if (estadoSelect) {
        estadoSelect.addEventListener('change', function() {
            console.log(`📊 Estado cambiado a: ${this.value}`);
            sincronizarEstadoActivo();
            // ❌ REMOVIDO: NO auto-enviar formulario
            // filtroForm.submit();
        });
    }
    
    if (activoSelect) {
        activoSelect.addEventListener('change', function() {
            console.log(`✅ Activo cambiado a: ${this.value}`);
            sincronizarEstadoActivo();
            // ❌ REMOVIDO: NO auto-enviar formulario
            // filtroForm.submit();
        });
    }
    
    // ✅ NUEVA FUNCIONALIDAD: Solo aplicar filtros cuando se hace clic en el botón
    const submitButton = filtroForm.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.addEventListener('click', function(e) {
            console.log('🔍 Aplicando filtros...');
            // El formulario se enviará normalmente
        });
    }
    
    // ✅ FUNCIONALIDAD: Prevenir envío accidental del formulario
    filtroForm.addEventListener('submit', function(e) {
        // Solo permitir envío si se hizo clic en el botón de submit
        if (!e.submitter || e.submitter.type !== 'submit') {
            console.log('⚠️ Envío de formulario bloqueado - debe usar el botón "Aplicar Filtros"');
            e.preventDefault();
            return false;
        }
        console.log('✅ Formulario enviado correctamente');
    });
    
    // Inicializar sincronización
    sincronizarEstadoActivo();
    
    // ✅ NUEVA FUNCIONALIDAD: Indicador visual de filtros activos
    function mostrarFiltrosActivos() {
        const filtrosActivos = [];
        
        if (edificioSelect && edificioSelect.value) {
            const edificioTexto = edificioSelect.options[edificioSelect.selectedIndex].text;
            filtrosActivos.push(`Edificio: ${edificioTexto}`);
        }
        
        if (pisoSelect && pisoSelect.value) {
            filtrosActivos.push(`Piso: ${pisoSelect.value}`);
        }
        
        if (estadoSelect && estadoSelect.value) {
            const estadoTexto = estadoSelect.options[estadoSelect.selectedIndex].text;
            filtrosActivos.push(`Estado: ${estadoTexto}`);
        }
        
        if (activoSelect && activoSelect.value && activoSelect.value !== 'true') {
            const activoTexto = activoSelect.options[activoSelect.selectedIndex].text;
            filtrosActivos.push(`Situación: ${activoTexto}`);
        }
        
        // Mostrar indicador si hay filtros activos
        let indicador = document.getElementById('filtros-activos-indicador');
        if (filtrosActivos.length > 0) {
            if (!indicador) {
                indicador = document.createElement('div');
                indicador.id = 'filtros-activos-indicador';
                indicador.className = 'alert alert-info alert-sm mt-2';
                filtroForm.appendChild(indicador);
            }
            indicador.innerHTML = `<i class="fas fa-filter me-2"></i><strong>Filtros activos:</strong> ${filtrosActivos.join(', ')}`;
        } else if (indicador) {
            indicador.remove();
        }
    }
    
    // ✅ NUEVA FUNCIONALIDAD: Mostrar contador de resultados
    function actualizarContadorResultados() {
        const tabla = document.querySelector('.table tbody');
        if (!tabla) return;
        
        const filas = tabla.querySelectorAll('tr');
        const filasVisibles = Array.from(filas).filter(fila => fila.style.display !== 'none').length;
        
        let contador = document.getElementById('contador-resultados');
        if (!contador) {
            contador = document.createElement('small');
            contador.id = 'contador-resultados';
            contador.className = 'text-muted';
            
            const cardBody = document.querySelector('.card .card-body');
            if (cardBody) {
                cardBody.insertBefore(contador, cardBody.firstChild);
            }
        }
        
        contador.textContent = `Mostrando ${filasVisibles} resultado${filasVisibles !== 1 ? 's' : ''}`;
    }
    
    // ✅ FUNCIONALIDAD ADICIONAL: Limpiar filtros con Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const url = new URL(window.location);
            url.search = '';
            window.location.href = url.toString();
        }
    });
    
    // ✅ FUNCIONALIDAD: Guardar preferencias de filtros en localStorage
    function guardarPreferenciasFiltros() {
        const preferencias = {
            edificio: edificioSelect ? edificioSelect.value : '',
            piso: pisoSelect ? pisoSelect.value : '',
            estado: estadoSelect ? estadoSelect.value : '',
            activo: activoSelect ? activoSelect.value : 'true'
        };
        
        localStorage.setItem('viviendas_filtros_preferencias', JSON.stringify(preferencias));
    }
    
    function cargarPreferenciasFiltros() {
        try {
            const preferencias = JSON.parse(localStorage.getItem('viviendas_filtros_preferencias') || '{}');
            
            // Solo aplicar preferencias si no hay parámetros en la URL
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.toString() === '') {
                if (edificioSelect && preferencias.edificio) {
                    edificioSelect.value = preferencias.edificio;
                    actualizarPisos();
                }
                if (estadoSelect && preferencias.estado) {
                    estadoSelect.value = preferencias.estado;
                }
                if (activoSelect && preferencias.activo) {
                    activoSelect.value = preferencias.activo;
                }
                sincronizarEstadoActivo();
            }
        } catch (error) {
            console.log('ℹ️ No se pudieron cargar las preferencias de filtros');
        }
    }
    
    // Cargar preferencias al inicio
    // cargarPreferenciasFiltros();
    
    // Guardar preferencias al aplicar filtros
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            guardarPreferenciasFiltros();
        });
    }
    
    console.log('✅ Filtros de viviendas inicializados correctamente');
});