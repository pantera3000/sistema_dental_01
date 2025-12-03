# auditoria/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LogAuditoria(models.Model):
    """Modelo para registrar todas las acciones del sistema"""
    
    ACCION_CHOICES = [
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('ELIMINAR', 'Eliminación'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('VER', 'Visualización'),
        ('EXPORTAR', 'Exportación'),
    ]
    
    # Usuario que realizó la acción
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='logs_auditoria'
    )
    usuario_nombre = models.CharField(max_length=150, blank=True)  # Backup si se elimina usuario
    
    # Acción realizada
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    
    # Modelo afectado
    modelo = models.CharField(max_length=100)  # Ej: "Paciente", "Cita", etc.
    objeto_id = models.IntegerField(null=True, blank=True)
    objeto_repr = models.CharField(max_length=200, blank=True)  # Representación del objeto
    
    # Detalles
    cambios = models.JSONField(null=True, blank=True)  # Cambios antes/después
    detalles = models.TextField(blank=True)  # Información adicional
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    fecha_hora = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        indexes = [
            models.Index(fields=['-fecha_hora']),
            models.Index(fields=['usuario', '-fecha_hora']),
            models.Index(fields=['modelo', '-fecha_hora']),
            models.Index(fields=['accion', '-fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.modelo} - {self.usuario_nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Guardar nombre de usuario como backup
        if self.usuario and not self.usuario_nombre:
            self.usuario_nombre = self.usuario.get_full_name() or self.usuario.username
        super().save(*args, **kwargs)
    
    @property
    def icono_accion(self):
        """Retorna el icono Bootstrap según la acción"""
        iconos = {
            'CREAR': 'bi-plus-circle-fill text-success',
            'EDITAR': 'bi-pencil-fill text-primary',
            'ELIMINAR': 'bi-trash-fill text-danger',
            'LOGIN': 'bi-box-arrow-in-right text-info',
            'LOGOUT': 'bi-box-arrow-left text-secondary',
            'VER': 'bi-eye-fill text-info',
            'EXPORTAR': 'bi-download text-warning',
        }
        return iconos.get(self.accion, 'bi-circle-fill')
    
    @property
    def badge_class(self):
        """Retorna la clase CSS del badge según la acción"""
        badges = {
            'CREAR': 'bg-success',
            'EDITAR': 'bg-primary',
            'ELIMINAR': 'bg-danger',
            'LOGIN': 'bg-info',
            'LOGOUT': 'bg-secondary',
            'VER': 'bg-info',
            'EXPORTAR': 'bg-warning',
        }
        return badges.get(self.accion, 'bg-secondary')
