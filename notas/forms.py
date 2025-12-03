# notas/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Nota, ImagenNota

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['paciente', 'titulo', 'contenido']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Recordatorio, Observación, etc.'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escribe aquí el contenido de la nota...'}),
        }

    def __init__(self, *args, **kwargs):
        paciente_id = kwargs.pop('paciente_id', None)
        super().__init__(*args, **kwargs)
        self.fields['paciente'].required = False
        self.fields['paciente'].empty_label = "— Nota general (sin paciente) —"
        if paciente_id:
            self.fields['paciente'].initial = paciente_id
            self.fields['paciente'].widget = forms.HiddenInput()


class ImagenNotaForm(forms.ModelForm):
    class Meta:
        model = ImagenNota
        fields = ['imagen', 'imagen_drive_url', 'descripcion']
        widgets = {
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'imagen_drive_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://drive.google.com/file/d/...',
            }),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Radiografía, foto clínica, etc.'}),
        }
        help_texts = {
            'imagen': 'Sube una imagen desde tu computadora',
            'imagen_drive_url': '📁 O pega el link de compartir de Google Drive (haz click en "Abrir Drive" para subir)',
        }


# Formset para manejar múltiples imágenes
ImagenNotaFormSet = inlineformset_factory(
    Nota,
    ImagenNota,
    form=ImagenNotaForm,
    extra=1,
    can_delete=True
)