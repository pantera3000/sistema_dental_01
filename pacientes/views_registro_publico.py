# pacientes/views_registro_publico.py
# Vista para registro público de pacientes (sin token)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Paciente
from .forms_registro_publico import RegistroPacientePublicoForm
from datetime import date


def registro_paciente_publico(request):
    """Formulario público para que pacientes se auto-registren"""
    
    if request.method == 'POST':
        form = RegistroPacientePublicoForm(request.POST)
        if form.is_valid():
            # Crear nuevo paciente
            paciente = Paciente.objects.create(
                nombre_completo=form.cleaned_data['nombre_completo'],
                dni=form.cleaned_data['dni'],
                fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                genero=form.cleaned_data['genero'],
                telefono=form.cleaned_data['telefono'],
                nombre_tutor=form.cleaned_data.get('nombre_tutor', ''),
                email=form.cleaned_data.get('email', ''),
                direccion=form.cleaned_data.get('direccion', ''),
                estado_civil='S',  # Por defecto soltero
                # Antecedentes médicos
                enfermedades_previas=form.cleaned_data.get('enfermedades_detalle', ''),
                alergias=form.cleaned_data.get('alergias_detalle', ''),
                # Observaciones con motivo de consulta
                observaciones=f"MOTIVO DE CONSULTA: {form.cleaned_data.get('motivo_consulta', 'No especificado')}\n\n"
                              f"Medicamentos: {form.cleaned_data.get('medicamentos_detalle', 'Ninguno')}"
            )
            
            return redirect('/registro-paciente/completado/')
    else:
        form = RegistroPacientePublicoForm()
    
    # Obtener configuración del consultorio
    from configuracion.models import ConfiguracionConsultorio
    try:
        config = ConfiguracionConsultorio.objects.first()
    except:
        config = None
    
    context = {
        'form': form,
        'config_consultorio': config,
    }
    
    return render(request, 'pacientes/registro_publico.html', context)


def registro_completado(request):
    """Página de confirmación después del registro"""
    return render(request, 'pacientes/registro_completado.html')
