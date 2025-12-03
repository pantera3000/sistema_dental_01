# pacientes/views_ficha_medica.py
# Vistas para el sistema de ficha médica pública

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Paciente, TokenFichaPaciente, FichaMedicaPaciente
from .forms import FichaMedicaPacienteForm


def generar_token_ficha(request, paciente_id):
    """Genera un token único para que el paciente llene su ficha médica"""
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Crear token
    token = TokenFichaPaciente.objects.create(paciente=paciente)
    
    # Construir URL completa
    url_ficha = request.build_absolute_uri(f'/ficha/{token.token}/')
    
    # Retornar JSON con el link
    return JsonResponse({
        'success': True,
        'token': token.token,
        'url': url_ficha,
        'expira_en': token.expira_en.strftime('%d/%m/%Y %H:%M'),
        'dias_validos': 7
    })


def ficha_publica(request, token):
    """Vista pública para que el paciente llene su ficha médica"""
    
    # Buscar token
    try:
        token_obj = TokenFichaPaciente.objects.get(token=token)
    except TokenFichaPaciente.DoesNotExist:
        return render(request, 'pacientes/ficha_error.html', {
            'error': 'Token inválido',
            'mensaje': 'Este enlace no es válido. Por favor contacta al consultorio.'
        })
    
    # Verificar si está vigente
    if not token_obj.esta_vigente:
        if token_obj.completado:
            return render(request, 'pacientes/ficha_error.html', {
                'error': 'Ficha ya completada',
                'mensaje': 'Esta ficha ya fue completada anteriormente. Gracias.'
            })
        else:
            return render(request, 'pacientes/ficha_error.html', {
                'error': 'Token expirado',
                'mensaje': f'Este enlace expiró el {token_obj.expira_en.strftime("%d/%m/%Y")}. Solicita uno nuevo al consultorio.'
            })
    
    paciente = token_obj.paciente
    
    if request.method == 'POST':
        form = FichaMedicaPacienteForm(request.POST)
        if form.is_valid():
            ficha = form.save(commit=False)
            ficha.paciente = paciente
            
            # Obtener IP del cliente
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            ficha.ip_completado = ip
            
            ficha.save()
            
            # Actualizar datos del paciente
            paciente.email = ficha.email
            paciente.direccion = ficha.direccion_completa
            paciente.ocupacion = ficha.ocupacion
            paciente.save()
            
            # Marcar token como completado
            token_obj.completado = True
            token_obj.completado_en = timezone.now()
            token_obj.ip_address = ip
            token_obj.save()
            
            return redirect('/ficha/completada/')
    else:
        # Pre-llenar con datos existentes del paciente
        initial_data = {
            'email': paciente.email,
            'direccion_completa': paciente.direccion,
            'ocupacion': paciente.ocupacion,
        }
        form = FichaMedicaPacienteForm(initial=initial_data)
    
    context = {
        'form': form,
        'paciente': paciente,
        'token': token_obj,
        'dias_restantes': token_obj.dias_restantes,
    }
    
    return render(request, 'pacientes/ficha_publica.html', context)


def ficha_completada(request):
    """Página de confirmación después de completar la ficha"""
    return render(request, 'pacientes/ficha_completada.html')
