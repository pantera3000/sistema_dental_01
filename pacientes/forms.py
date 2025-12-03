# pacientes/forms.py

from django import forms
from .models import Paciente, FichaMedicaPaciente


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Juan Pérez López'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '8 dígitos'
            }),
            'fecha_nacimiento': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 987654321'
            }),
            'distrito': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Miraflores'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@email.com'
            }),
            'ocupacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Profesor, Estudiante, etc.'
            }),
            'nombre_tutor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Solo si el paciente es menor de edad'
            }),
            'enfermedades_previas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ej: Diabetes, hipertensión, etc.'
            }),
            'alergias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ej: Penicilina, latex, etc.'
            }),
            'grupo_sanguineo': forms.Select(attrs={'class': 'form-select'}),
            'tratamientos_previos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ej: Endodoncia en 2020, implantes, etc.'
            }),
            'experiencias_dentales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ej: Miedo al dentista, ansiedad, etc.'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cualquier información adicional'
            }),
        }


# ============================================
# FORMULARIO DE FICHA MÉDICA PÚBLICA
# ============================================

class FichaMedicaPacienteForm(forms.ModelForm):
    class Meta:
        model = FichaMedicaPaciente
        exclude = ['paciente', 'fecha_completado', 'ip_completado']
        widgets = {
            # Datos personales
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'direccion_completa': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'required': True}),
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Antecedentes médicos
            'tiene_enfermedades': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enfermedades_detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'toma_medicamentos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'medicamentos_detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tiene_alergias': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alergias_detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'esta_embarazada': forms.NullBooleanSelect(attrs={'class': 'form-select'}),
            'tiene_cirugias_previas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cirugias_detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            
            # Antecedentes dentales
            'ultima_visita_dentista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tiene_tratamientos_previos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tratamientos_previos_detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'problemas_dentales_actuales': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            
            # Consentimientos
            'acepta_tratamiento_datos': forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': True}),
            'acepta_contacto': forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': True}),
        }