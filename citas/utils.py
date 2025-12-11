import requests
from ics import Calendar
import pytz
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

def get_calendar_events():
    """
    Fetches and processes events from the Google Calendar ICS URL.
    Returns a list of event objects with timezone-aware 'local_begin' attribute.
    """
    # URL del ICS (Calendario privado o público)
    ics_url = "https://calendar.google.com/calendar/ical/juancarloscn%40gmail.com/private-7c3dfb4a8b649579159a76228916d6cf/basic.ics "
    
    events = []
    
    # Intentar obtener el contenido crudo (texto) del caché
    # Cacheamos el TEXTO, no los objetos, para evitar error "pickle"
    cache_key = 'calendar_ics_raw_content'
    ics_text = cache.get(cache_key)
    
    if not ics_text:
        try:
            # Timeout de 5s para no bloquear el sistema si Google falla
            response = requests.get(ics_url, timeout=5)
            response.raise_for_status()
            ics_text = response.text
            
            # Guardar en caché por 15 minutos (900 segundos)
            cache.set(cache_key, ics_text, 900)
            
        except Exception as e:
            print(f"Error fetching calendar: {e}")
            return []

    try:
        c = Calendar(ics_text)
        
        # Configurar zona horaria
        limatz = pytz.timezone('America/Lima')
        
        for event in c.events:
            # Convertir a datetime con zona horaria si es necesario
            if hasattr(event.begin, 'datetime'):
                event_dt = event.begin.datetime
            else:
                event_dt = event.begin
            
            # Asegurar que tenga zona horaria
            if event_dt.tzinfo is None:
                event_dt = pytz.utc.localize(event_dt)
            
            # Convertir a Lima
            event_local = event_dt.astimezone(limatz)
            
            # Asignar fecha local al evento
            event.local_begin = event_local
            
            events.append(event)
            
        # Ordenar eventos por fecha
        events.sort(key=lambda x: x.local_begin)
        
    except Exception as e:
        print(f"Error fetching calendar: {e}")
        # En caso de error devolvemos lista vacía para no romper la vista
        return []
        
    return events
