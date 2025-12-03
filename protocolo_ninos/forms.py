from django import forms
from .models import EvaluacionFuncional

class EvaluacionFuncionalForm(forms.ModelForm):
    class Meta:
        model = EvaluacionFuncional
        exclude = ['paciente', 'fecha_creacion', 'fecha_actualizacion']
        widgets = {
            # Ventana Nasal
            'ventana_nasal_mas_cerrada': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'ventana_nasal_respira_mejor': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Patrón de Crecimiento
            'patron_crecimiento': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Oclusión
            'maloclusion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'mordida_cruzada': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'sobremordida': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Amígdalas
            'amigdalas_grado': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'amigdalas_mas_inflamada': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Capacidad Masticatoria
            'tiempo_comer': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'lengua_boca_abierta': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Alergias e Historial
            'resfrios_ultimo_anio': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'enfermedades_respiratorias': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'antibioticos_ultimo_anio': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Sueño y Respiración
            'respiracion_nocturna': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'movilidad_dormir': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'bruxismo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'recuperacion_despertar': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Evaluación de Funciones
            'eval_masticacion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'eval_respiracion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'eval_deglucion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Evaluación Neurovegetativa
            'fonacion': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'actividad_fisica': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'habitos_alimentarios': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'horas_pantallas': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Plan de Tratamiento
            'plan_comer_lado_preferente': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # Text Areas
            'antecedentes_interes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'enfermedad_actual': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medicacion_actual': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alergico_a_que': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clase form-check-input a todos los booleanos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
