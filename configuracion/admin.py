# configuracion/admin.py
from django.contrib import admin
from .models import ConfiguracionConsultorio

@admin.register(ConfiguracionConsultorio)
class ConfiguracionConsultorioAdmin(admin.ModelAdmin):
    list_display = ['nombre_consultorio', 'titulo_pdf', 'actualizado_en']
    fieldsets = (
        ('Información del PDF', {
            'fields': ('nombre_consultorio', 'titulo_pdf', 'logo')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono', 'email'),
            'classes': ('collapse',)
        }),
    )
