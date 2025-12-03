from django import forms
from .models import ProgramaSalud

class ProgramaSaludForm(forms.ModelForm):
    class Meta:
        model = ProgramaSalud
        exclude = ['paciente', 'fecha_creacion', 'fecha_actualizacion']
        widgets = {
            # Radios
            'masticacion_lado': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'ventana_nasal_predominante': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Text Areas
            'otras_patologias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medicacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'intervenciones_previas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ejercicio_fisico_antecedentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            
            # Text Inputs
            'placa_talla': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'nariz_talla': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clase form-check-input a todos los checkboxes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
