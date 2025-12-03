# usuarios/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rol"
    )
    telefono = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'grupo', 'telefono')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Asignar grupo
            grupo = self.cleaned_data['grupo']
            user.groups.add(grupo)
            
            # Actualizar perfil
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.save()
        
        return user


class UserEditForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rol"
    )
    telefono = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Pre-seleccionar el grupo actual
            grupos = self.instance.groups.all()
            if grupos.exists():
                self.fields['grupo'].initial = grupos.first()
            
            # Pre-llenar teléfono
            if hasattr(self.instance, 'perfil'):
                self.fields['telefono'].initial = self.instance.perfil.telefono
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Actualizar grupo
            if self.cleaned_data.get('grupo'):
                user.groups.clear()
                user.groups.add(self.cleaned_data['grupo'])
            
            # Actualizar perfil
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.save()
        
        return user
