from django.contrib import admin
from .models import Paciente, TokenFichaPaciente, FichaMedicaPaciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'dni', 'telefono', 'edad', 'creado_en')
    search_fields = ('nombre_completo', 'dni', 'telefono')
    list_filter = ('genero', 'estado_civil')


@admin.register(TokenFichaPaciente)
class TokenFichaPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'token', 'creado_en', 'expira_en', 'completado', 'dias_restantes')
    list_filter = ('completado', 'creado_en')
    search_fields = ('paciente__nombre_completo', 'token')
    readonly_fields = ('token', 'creado_en', 'completado_en', 'ip_address')
    
    def dias_restantes(self, obj):
        return f"{obj.dias_restantes} días"
    dias_restantes.short_description = "Días restantes"


@admin.register(FichaMedicaPaciente)
class FichaMedicaPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'email', 'fecha_completado', 'acepta_tratamiento_datos')
    search_fields = ('paciente__nombre_completo', 'email')
    list_filter = ('fecha_completado', 'acepta_tratamiento_datos', 'acepta_contacto')
    readonly_fields = ('fecha_completado', 'ip_completado')
