from django.shortcuts import render
import requests
from ics import Calendar
from django.utils import timezone
from datetime import timedelta
import pytz

def calendario_view(request):
    # Placeholder for the Embed URL
    # The user should replace this with their specific Embed URL
    calendar_embed_url = "https://calendar.google.com/calendar/embed?src=es.pe%23holiday%40group.v.calendar.google.com&ctz=America%2FLima"
    return render(request, 'citas/calendario.html', {'calendar_embed_url': calendar_embed_url})

def lista_eventos_view(request):
    from .utils import get_calendar_events
    
    today_events = []
    filtered_events = []
    error_message = None
    filter_type = request.GET.get('filter', 'week') # Default filter: week (optimized for performance)

    try:
        # Obtener eventos usando la utilidad compartida
        all_events = get_calendar_events()
        
        # Configurar zona horaria y fechas
        limatz = pytz.timezone('America/Lima')
        now = timezone.now().astimezone(limatz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Definir rango de fechas para el filtro
        if filter_type == 'week':
            # Semana actual (Lunes a Domingo)
            start_date = today_start - timedelta(days=today_start.weekday())
            end_date = start_date + timedelta(days=7)
        elif filter_type == 'month':
            # Mes actual
            start_date = today_start.replace(day=1)
            # Primer día del próximo mes
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        elif filter_type == 'last_month':
            # Mes pasado
            this_month_start = today_start.replace(day=1)
            if this_month_start.month == 1:
                start_date = this_month_start.replace(year=this_month_start.year - 1, month=12)
            else:
                start_date = this_month_start.replace(month=this_month_start.month - 1)
            end_date = this_month_start
        elif filter_type == 'next_3_months':
            # Próximos 3 meses
            start_date = today_start
            end_date = start_date + timedelta(days=90)
        else:
            # Fallback a mes actual
            start_date = today_start.replace(day=1)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)

        # Procesar eventos
        for event in all_events:
            event_local = event.local_begin
            
            # Filtrar eventos de HOY
            if today_start <= event_local < today_end:
                today_events.append(event)
            
            # Filtrar eventos según el filtro seleccionado
            if start_date <= event_local < end_date:
                filtered_events.append(event)
                
    except Exception as e:
        error_message = f"Error al procesar eventos: {e}"

    context = {
        'today_events': today_events,
        'filtered_events': filtered_events,
        'current_filter': filter_type,
        'error_message': error_message,
        'now': now # Para mostrar la fecha actual si se desea
    }
    return render(request, 'citas/lista_eventos.html', context)
