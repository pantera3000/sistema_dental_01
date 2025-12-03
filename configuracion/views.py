# configuracion/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ConfiguracionConsultorio
from .forms import ConfiguracionConsultorioForm

def configuracion_view(request):
    """Vista para editar la configuración del consultorio"""
    config = ConfiguracionConsultorio.get_configuracion()
    
    if request.method == 'POST':
        form = ConfiguracionConsultorioForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Configuración guardada exitosamente')
            return redirect('configuracion:configuracion')
    else:
        form = ConfiguracionConsultorioForm(instance=config)
    
    return render(request, 'configuracion/configuracion.html', {
        'form': form,
        'config': config
    })
