# auditoria/admin.py
from django.contrib import admin
from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'usuario_nombre', 'accion', 'modelo', 'objeto_repr', 'ip_address']
    list_filter = ['accion', 'modelo', 'fecha_hora']
    search_fields = ['usuario_nombre', 'objeto_repr', 'detalles', 'ip_address']
    readonly_fields = ['usuario', 'usuario_nombre', 'accion', 'modelo', 'objeto_id', 
                       'objeto_repr', 'cambios', 'detalles', 'ip_address', 'user_agent', 'fecha_hora']
    date_hierarchy = 'fecha_hora'
    
    def has_add_permission(self, request):
        return False  # No se pueden crear logs manualmente
    
    def has_delete_permission(self, request, obj=None):
        return False  # No se pueden eliminar logs
    
    def has_change_permission(self, request, obj=None):
        return False  # No se pueden editar logs
