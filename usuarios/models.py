from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='usuarios/fotos/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_rol(self):
        if self.user.is_superuser:
            return "Superusuario"
        grupos = self.user.groups.all()
        if grupos.exists():
            return grupos.first().name
        return "Sin rol"
