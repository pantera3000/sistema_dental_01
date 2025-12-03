# pacientes/forms.py - AGREGAR al final del archivo

from django import forms
from .models import Paciente


class RegistroPacientePublicoForm(forms.Form):
    """Formulario público para auto-registro de pacientes"""
    
    # Datos básicos del paciente
    nombre_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez López'})
    )
    dni = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '8 dígitos'})
    )
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    genero = forms.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    telefono = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '987654321'})
    )
    nombre_tutor = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nombre completo del padre/madre/tutor',
            'id': 'id_nombre_tutor'
        })
    )
    email = forms.EmailField(
        required=False,  # Opcional
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'})
    )
    direccion = forms.CharField(
        required=False,  # Opcional
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa'})
    )
    
    # Antecedentes médicos
    tiene_enfermedades = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    enfermedades_detalle = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Especifique cuál(es)'})
    )
    
    tiene_alergias = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    alergias_detalle = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Especifique a qué'})
    )
    
    toma_medicamentos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    medicamentos_detalle = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Especifique cuál(es)'})
    )
    
    # Motivo de consulta - AHORA OPCIONAL
    motivo_consulta = forms.CharField(
        required=False,  # Opcional
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '¿Por qué desea agendar una cita? (opcional)'})
    )
    
    # Consentimientos
    acepta_tratamiento_datos = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    acepta_contacto = forms.BooleanField(
        required=False,  # Opcional
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números")
        if len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener 8 dígitos")
        # Verificar si ya existe
        if Paciente.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un paciente con este DNI. Por favor contacta al consultorio.")
        return dni
