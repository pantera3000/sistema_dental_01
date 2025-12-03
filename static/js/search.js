// static/js/search.js
/**
 * Búsqueda Global
 * Maneja la búsqueda en tiempo real con debounce
 */

(function() {
    'use strict';
    
    // Elementos del DOM
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) {
        console.warn('Elementos de búsqueda no encontrados');
        return;
    }
    
    // Variables de control
    let searchTimeout;
    const DEBOUNCE_DELAY = 300; // ms
    const MIN_QUERY_LENGTH = 2;
    
    /**
     * Renderiza los resultados de búsqueda
     */
    function renderSearchResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = `
                <div class="search-result-item">
                    <div class="search-result-title">No se encontraron resultados</div>
                    <div class="search-result-meta">Intenta con otro término</div>
                </div>
            `;
        } else {
            searchResults.innerHTML = results.map(result => `
                <a href="${result.url}" class="search-result-item">
                    <i class="bi ${result.icon} search-result-icon"></i>
                    <div class="search-result-content">
                        <div class="search-result-title">${escapeHtml(result.title)}</div>
                        <div class="search-result-meta">${escapeHtml(result.subtitle)}</div>
                    </div>
                    <span class="search-result-badge">${escapeHtml(result.type)}</span>
                </a>
            `).join('');
        }
        
        searchResults.classList.add('show');
    }
    
    /**
     * Escapa HTML para prevenir XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Realiza la búsqueda AJAX
     */
    function performSearch(query) {
        fetch(`/pacientes/api/buscar/?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la búsqueda');
                }
                return response.json();
            })
            .then(data => {
                renderSearchResults(data.results);
            })
            .catch(error => {
                console.error('Error en búsqueda:', error);
                searchResults.innerHTML = `
                    <div class="search-result-item">
                        <div class="search-result-title">Error al buscar</div>
                        <div class="search-result-meta">Intenta nuevamente</div>
                    </div>
                `;
                searchResults.classList.add('show');
            });
    }
    
    /**
     * Maneja el evento de input con debounce
     */
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        // Si la query es muy corta, ocultar resultados
        if (query.length < MIN_QUERY_LENGTH) {
            searchResults.classList.remove('show');
            return;
        }
        
        // Debounce: esperar antes de buscar
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, DEBOUNCE_DELAY);
    });
    
    /**
     * Cerrar resultados al hacer click fuera
     */
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('show');
        }
    });
    
    /**
     * Mostrar resultados al hacer focus si hay query
     */
    searchInput.addEventListener('focus', function() {
        const query = this.value.trim();
        if (query.length >= MIN_QUERY_LENGTH && searchResults.children.length > 0) {
            searchResults.classList.add('show');
        }
    });
    
    /**
     * Navegación con teclado en resultados
     */
    let selectedIndex = -1;
    
    searchInput.addEventListener('keydown', function(e) {
        const items = searchResults.querySelectorAll('.search-result-item');
        
        if (items.length === 0) return;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = (selectedIndex + 1) % items.length;
                updateSelection(items);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = selectedIndex <= 0 ? items.length - 1 : selectedIndex - 1;
                updateSelection(items);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && items[selectedIndex]) {
                    items[selectedIndex].click();
                }
                break;
                
            case 'Escape':
                searchResults.classList.remove('show');
                selectedIndex = -1;
                break;
        }
    });
    
    /**
     * Actualiza la selección visual
     */
    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }
    
    console.log('✓ Búsqueda global inicializada');
})();
