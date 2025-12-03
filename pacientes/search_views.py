# pacientes/search_views.py
"""
Vistas para búsqueda global en el sistema
"""

from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q

from .models import Paciente
from tratamientos.models import Tratamiento

try:
    from historias.models import HistoriaClinica
    HISTORIAS_AVAILABLE = True
except ImportError:
    HISTORIAS_AVAILABLE = False


def busqueda_global(request):
    """
    Vista AJAX para búsqueda global
    Busca en pacientes, tratamientos e historias clínicas
    
    Parámetros GET:
        q: término de búsqueda (mínimo 2 caracteres)
    
    Retorna:
        JSON con lista de resultados, cada uno con:
        - type: tipo de resultado (paciente/tratamiento/historia)
        - title: título principal
        - subtitle: información adicional
        - url: URL para navegar al detalle
        - icon: clase de icono Bootstrap
    """
    query = request.GET.get('q', '').strip()
    
    # Validar longitud mínima
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # ===== BUSCAR EN PACIENTES =====
    pacientes = Paciente.objects.filter(
        Q(nombre__icontains=query) |
        Q(apellido__icontains=query) |
        Q(dni__icontains=query)
    )[:5]  # Limitar a 5 resultados
    
    for p in pacientes:
        results.append({
            'type': 'paciente',
            'title': p.nombre_completo,
            'subtitle': f'DNI: {p.dni}' if p.dni else 'Sin DNI',
            'url': reverse('pacientes:detalle', args=[p.id]),
            'icon': 'bi-person'
        })
    
    # ===== BUSCAR EN TRATAMIENTOS =====
    tratamientos = Tratamiento.objects.filter(
        Q(descripcion__icontains=query) |
        Q(paciente__nombre__icontains=query) |
        Q(paciente__apellido__icontains=query)
    ).select_related('paciente')[:5]
    
    for t in tratamientos:
        results.append({
            'type': 'tratamiento',
            'title': t.descripcion,
            'subtitle': f'Paciente: {t.paciente.nombre_completo}',
            'url': reverse('tratamientos:detalle', args=[t.id]),
            'icon': 'bi-heart-pulse'
        })
    
    # ===== BUSCAR EN HISTORIAS CLÍNICAS =====
    if HISTORIAS_AVAILABLE:
        try:
            historias = HistoriaClinica.objects.filter(
                Q(diagnostico__icontains=query) |
                Q(tratamiento__icontains=query) |
                Q(paciente__nombre__icontains=query) |
                Q(paciente__apellido__icontains=query)
            ).select_related('paciente')[:5]
            
            for h in historias:
                # Truncar diagnóstico si es muy largo
                diagnostico_preview = h.diagnostico[:50] + '...' if len(h.diagnostico) > 50 else h.diagnostico
                results.append({
                    'type': 'historia',
                    'title': f'Historia - {h.paciente.nombre_completo}',
                    'subtitle': diagnostico_preview,
                    'url': reverse('historias:detalle', args=[h.id]),
                    'icon': 'bi-journal-medical'
                })
        except Exception as e:
            # Si hay algún error, simplemente no agregamos historias
            print(f"Error buscando en historias: {e}")
    
    return JsonResponse({'results': results})
