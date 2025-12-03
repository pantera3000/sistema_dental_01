# configuracion/context_processors.py
from .models import ConfiguracionConsultorio

def configuracion_consultorio(request):
    """Context processor para hacer disponible la configuración en todos los templates"""
    config = ConfiguracionConsultorio.get_configuracion()
    return {
        'config_consultorio': config
    }
