# citas/context_processors.py
from django.utils import timezone
import pytz
from datetime import timedelta
from .utils import get_calendar_events

def citas_pendientes_hoy(request):
    """
    Context processor para mostrar citas pendientes del día actual.
    Solo muestra citas que aún no han pasado (futuras respecto a la hora actual).
    """
    citas_pendientes = []
    
    try:
        # Obtener todos los eventos del calendario
        all_events = get_calendar_events()
        
        # Configurar zona horaria
        limatz = pytz.timezone('America/Lima')
        now = timezone.now().astimezone(limatz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Filtrar eventos de hoy que aún no han pasado
        for event in all_events:
            event_local = event.local_begin
            
            # Solo eventos de hoy que son futuros (aún no han pasado)
            if today_start <= event_local < today_end and event_local > now:
                citas_pendientes.append(event)
        
        # Ordenar por hora
        citas_pendientes.sort(key=lambda x: x.local_begin)
        
    except Exception as e:
        print(f"Error obteniendo citas pendientes: {e}")
        citas_pendientes = []
    
    return {
        'citas_pendientes_hoy': citas_pendientes,
        'citas_pendientes_count': len(citas_pendientes)
    }
