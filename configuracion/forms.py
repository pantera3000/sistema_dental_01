# configuracion/forms.py
from django import forms
from .models import ConfiguracionConsultorio

class ConfiguracionConsultorioForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionConsultorio
        fields = ['nombre_consultorio', 'titulo_pdf', 'logo', 'direccion', 'telefono', 'email']
        widgets = {
            'nombre_consultorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Clínica Dental Sonrisas'
            }),
            'titulo_pdf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ODONTOGRAMA'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
        }
