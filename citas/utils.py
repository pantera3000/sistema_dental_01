import requests
from ics import Calendar
import pytz
from django.utils import timezone
from datetime import timedelta

def get_calendar_events():
    """
    Fetches and processes events from the Google Calendar ICS URL.
    Returns a list of event objects with timezone-aware 'local_begin' attribute.
    """
    # URL del ICS (Calendario privado o público)
    ics_url = "https://calendar.google.com/calendar/ical/juancarloscn%40gmail.com/private-7c3dfb4a8b649579159a76228916d6cf/basic.ics"
    
    events = []
    try:
        response = requests.get(ics_url)
        response.raise_for_status()
        c = Calendar(response.text)
        
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
