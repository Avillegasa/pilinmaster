/**
 * SIDEBAR MEJORADO - JavaScript
 * Funcionalidades: Scroll, búsqueda, colapso inteligente, responsive
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // CONFIGURACIÓN INICIAL
    // ==========================================
    
    const sidebar = document.getElementById('sidebarMenu');
    const sidebarSearch = document.getElementById('sidebarSearch');
    const sidebarContent = document.querySelector('.sidebar-content');
    const sidebarToggles = document.querySelectorAll('.sidebar-toggle');
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    
    // ==========================================
    // FUNCIONALIDAD DE BÚSQUEDA
    // ==========================================
    
    if (sidebarSearch) {
        sidebarSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            const sidebarSections = document.querySelectorAll('.sidebar-section');
            
            if (searchTerm === '') {
                // Mostrar todas las secciones
                sidebarSections.forEach(section => {
                    section.style.display = 'block';
                    const links = section.querySelectorAll('.sidebar-link');
                    links.forEach(link => {
                        link.style.display = 'flex';
                        link.classList.remove('search-highlight');
                    });
                });
            } else {
                // Filtrar por término de búsqueda
                sidebarSections.forEach(section => {
                    const links = section.querySelectorAll('.sidebar-link');
                    let hasVisibleLinks = false;
                    
                    links.forEach(link => {
                        const linkText = link.textContent.toLowerCase();
                        if (linkText.includes(searchTerm)) {
                            link.style.display = 'flex';
                            link.classList.add('search-highlight');
                            hasVisibleLinks = true;
                        } else {
                            link.style.display = 'none';
                            link.classList.remove('search-highlight');
                        }
                    });
                    
                    // Mostrar/ocultar sección completa
                    section.style.display = hasVisibleLinks ? 'block' : 'none';
                    
                    // Expandir secciones con resultados
                    if (hasVisibleLinks) {
                        const collapse = section.querySelector('.collapse');
                        if (collapse) {
                            collapse.classList.add('show');
                        }
                    }
                });
            }
        });
    }
    
    // ==========================================
    // MANEJO DE COLAPSO INTELIGENTE
    // ==========================================
    
    function initCollapseBehavior() {
        const isMobile = window.innerWidth < 768;
        
        if (isMobile) {
            // En móvil: colapsar todas las secciones excepto la activa
            const activeSections = [];
            
            sidebarLinks.forEach(link => {
                if (link.classList.contains('active')) {
                    const section = link.closest('.sidebar-section');
                    const collapse = section?.querySelector('.collapse');
                    if (collapse) {
                        activeSections.push(collapse);
                    }
                }
            });
            
            // Colapsar todas las secciones
            document.querySelectorAll('.sidebar-section .collapse').forEach(collapse => {
                if (!activeSections.includes(collapse)) {
                    collapse.classList.remove('show');
                }
            });
        } else {
            // En desktop: mostrar todas las secciones principales
            document.querySelectorAll('.sidebar-section .collapse').forEach((collapse, index) => {
                if (index < 3) { // Mostrar las primeras 3 secciones (Principal, Acceso, Personal)
                    collapse.classList.add('show');
                }
            });
        }
    }
    
    // ==========================================
    // MANEJO DE TOGGLES DE SECCIÓN
    // ==========================================
    
    sidebarToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-bs-target');
            const targetElement = document.querySelector(targetId);
            const icon = this.querySelector('.transition-icon');
            
            if (targetElement) {
                const isExpanded = targetElement.classList.contains('show');
                
                // Animar icono
                if (icon) {
                    icon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
                }
                
                // En móvil, colapsar otras secciones al abrir una nueva
                if (window.innerWidth < 768 && !isExpanded) {
                    document.querySelectorAll('.sidebar-section .collapse.show').forEach(openCollapse => {
                        if (openCollapse !== targetElement) {
                            openCollapse.classList.remove('show');
                            // Resetear icono de la sección que se cierra
                            const otherToggle = document.querySelector(`[data-bs-target="#${openCollapse.id}"] .transition-icon`);
                            if (otherToggle) {
                                otherToggle.style.transform = 'rotate(0deg)';
                            }
                        }
                    });
                }
                
                // Toggle de la sección actual
                targetElement.classList.toggle('show');
            }
        });
    });
    
    // ==========================================
    // SCROLL SUAVE Y NAVEGACIÓN
    // ==========================================
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remover clase active de todos los enlaces
            sidebarLinks.forEach(l => l.classList.remove('active'));
            
            // Agregar clase active al enlace clickeado
            this.classList.add('active');
            
            // En móvil, cerrar sidebar después de hacer clic
            if (window.innerWidth < 768) {
                setTimeout(() => {
                    if (sidebar.classList.contains('show')) {
                        sidebar.classList.remove('show');
                    }
                }, 300);
            }
            
            // Guardar selección en localStorage
            localStorage.setItem('activeNavLink', this.getAttribute('href'));
        });
    });
    
    // ==========================================
    // RESTAURAR ESTADO ACTIVO
    // ==========================================
    
    function restoreActiveState() {
        const currentPath = window.location.pathname;
        const savedPath = localStorage.getItem('activeNavLink');
        
        // Primero intentar con la URL actual
        let activeLink = Array.from(sidebarLinks).find(link => {
            const href = link.getAttribute('href');
            return href && currentPath.startsWith(href) && href !== '/';
        });
        
        // Si no se encuentra, usar la guardada en localStorage
        if (!activeLink && savedPath) {
            activeLink = document.querySelector(`a[href="${savedPath}"]`);
        }
        
        // Aplicar estado activo
        if (activeLink) {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            activeLink.classList.add('active');
            
            // Expandir la sección que contiene el enlace activo
            const section = activeLink.closest('.sidebar-section');
            const collapse = section?.querySelector('.collapse');
            if (collapse && window.innerWidth < 768) {
                collapse.classList.add('show');
            }
        }
    }
    
    // ==========================================
    // SCROLL INTELIGENTE
    // ==========================================
    
    function initSmoothScroll() {
        if (sidebarContent) {
            // Scroll suave al hacer clic en enlaces
            sidebarContent.addEventListener('click', function(e) {
                if (e.target.closest('.sidebar-link')) {
                    // Pequeña animación de feedback
                    const link = e.target.closest('.sidebar-link');
                    link.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        link.style.transform = '';
                    }, 150);
                }
            });
            
            // Auto-scroll para mantener el enlace activo visible
            const activeLink = document.querySelector('.sidebar-link.active');
            if (activeLink) {
                setTimeout(() => {
                    activeLink.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest'
                    });
                }, 100);
            }
        }
    }
    
    // ==========================================
    // RESPONSIVE HANDLER
    // ==========================================
    
    function handleResize() {
        const isMobile = window.innerWidth < 768;
        
        if (isMobile) {
            // Configuración para móvil
            document.querySelectorAll('.sidebar-toggle').forEach(toggle => {
                toggle.style.display = 'block';
            });
            
            // Colapsar secciones no activas
            initCollapseBehavior();
        } else {
            // Configuración para desktop
            document.querySelectorAll('.sidebar-toggle').forEach(toggle => {
                toggle.style.display = 'none';
            });
            
            // Mostrar secciones principales
            document.querySelectorAll('.sidebar-section .collapse').forEach((collapse, index) => {
                if (index < 3) {
                    collapse.classList.add('show');
                }
            });
        }
    }
    
    // ==========================================
    // EFECTOS VISUALES
    // ==========================================
    
    function initVisualEffects() {
        // Efecto de hover mejorado
        sidebarLinks.forEach((link, index) => {
            link.style.animationDelay = `${index * 0.05}s`;
            
            link.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(8px) scale(1.02)';
            });
            
            link.addEventListener('mouseleave', function() {
                if (!this.classList.contains('active')) {
                    this.style.transform = 'translateX(0) scale(1)';
                }
            });
        });
        
        // Indicador de scroll
        if (sidebarContent) {
            let scrollTimeout;
            
            sidebarContent.addEventListener('scroll', function() {
                // Mostrar indicador de scroll
                this.classList.add('scrolling');
                
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    this.classList.remove('scrolling');
                }, 1000);
            });
        }
    }
    
    // ==========================================
    // ACCESIBILIDAD
    // ==========================================
    
    function initAccessibility() {
        // Navegación por teclado
        sidebarLinks.forEach(link => {
            link.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });
        
        // Manejo de focus
        sidebar.addEventListener('focusin', function() {
            this.classList.add('keyboard-focus');
        });
        
        sidebar.addEventListener('focusout', function() {
            setTimeout(() => {
                if (!this.contains(document.activeElement)) {
                    this.classList.remove('keyboard-focus');
                }
            }, 100);
        });
    }
    
    // ==========================================
    // GESTIÓN DE ESTADO LOCAL
    // ==========================================
    
    function saveCollapsedState() {
        const collapsedSections = [];
        document.querySelectorAll('.sidebar-section .collapse').forEach((collapse, index) => {
            if (!collapse.classList.contains('show')) {
                collapsedSections.push(index);
            }
        });
        localStorage.setItem('collapsedSections', JSON.stringify(collapsedSections));
    }
    
    function restoreCollapsedState() {
        const savedState = localStorage.getItem('collapsedSections');
        if (savedState && window.innerWidth >= 768) {
            const collapsedSections = JSON.parse(savedState);
            document.querySelectorAll('.sidebar-section .collapse').forEach((collapse, index) => {
                if (collapsedSections.includes(index)) {
                    collapse.classList.remove('show');
                } else {
                    collapse.classList.add('show');
                }
            });
        }
    }
    
    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    
    function initSidebar() {
        console.log('🚀 Inicializando sidebar mejorado...');
        
        // Inicializar comportamiento de colapso
        initCollapseBehavior();
        
        // Restaurar estados
        restoreActiveState();
        restoreCollapsedState();
        
        // Inicializar funcionalidades
        initSmoothScroll();
        initVisualEffects();
        initAccessibility();
        
        // Configurar responsive
        handleResize();
        
        console.log('✅ Sidebar inicializado correctamente');
    }
    
    // ==========================================
    // EVENT LISTENERS
    // ==========================================
    
    // Resize handler
    window.addEventListener('resize', debounce(handleResize, 250));
    
    // Guardar estado al cambiar
    document.addEventListener('click', function(e) {
        if (e.target.closest('.sidebar-toggle')) {
            setTimeout(saveCollapsedState, 100);
        }
    });
    
    // Prevenir cierre accidental en móvil
    sidebar.addEventListener('touchmove', function(e) {
        e.stopPropagation();
    });
    
    // ==========================================
    // UTILIDADES
    // ==========================================
    
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
    
    // ==========================================
    // INICIALIZAR TODO
    // ==========================================
    
    // Inicializar con un pequeño delay para asegurar que el DOM esté listo
    setTimeout(initSidebar, 100);
    
    // API pública para control externo
    window.SidebarController = {
        openSection: function(sectionId) {
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.add('show');
            }
        },
        closeSection: function(sectionId) {
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.remove('show');
            }
        },
        setActiveLink: function(href) {
            const link = document.querySelector(`a[href="${href}"]`);
            if (link) {
                sidebarLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                localStorage.setItem('activeNavLink', href);
            }
        },
        resetSearch: function() {
            if (sidebarSearch) {
                sidebarSearch.value = '';
                sidebarSearch.dispatchEvent(new Event('input'));
            }
        }
    };
});