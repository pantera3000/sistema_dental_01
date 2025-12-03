# usuarios/management/commands/setup_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Crea los grupos de usuarios y asigna permisos'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando grupos y asignando permisos...')
        
        # Definir grupos y sus permisos
        grupos_permisos = {
            'Superusuario': {
                'descripcion': 'Acceso total al sistema',
                'permisos': 'all'  # Todos los permisos
            },
            'Administrador': {
                'descripcion': 'Gestión completa del consultorio',
                'modelos': {
                    'paciente': ['view', 'add', 'change', 'delete'],
                    'entradahistoria': ['view', 'add', 'change', 'delete'],
                    'tratamiento': ['view', 'add', 'change', 'delete'],
                    'pago': ['view', 'add', 'change', 'delete'],
                    'nota': ['view', 'add', 'change', 'delete'],
                    'estadodiente': ['view', 'add', 'change'],
                    'historialodontograma': ['view'],
                    'configuracionconsultorio': ['view', 'change'],
                }
            },
            'Doctor': {
                'descripcion': 'Gestión de pacientes y tratamientos',
                'modelos': {
                    'paciente': ['view', 'add', 'change'],
                    'entradahistoria': ['view', 'add', 'change'],
                    'tratamiento': ['view', 'add', 'change'],
                    'pago': ['view'],
                    'nota': ['view', 'add', 'change'],
                    'estadodiente': ['view', 'add', 'change'],
                    'historialodontograma': ['view'],
                }
            },
            'Asistente': {
                'descripcion': 'Solo lectura y gestión de citas',
                'modelos': {
                    'paciente': ['view'],
                    'tratamiento': ['view'],
                    'nota': ['view'],
                    'estadodiente': ['view'],
                }
            }
        }
        
        for grupo_nombre, config in grupos_permisos.items():
            # Crear o obtener el grupo
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Grupo "{grupo_nombre}" creado'))
            else:
                self.stdout.write(f'  Grupo "{grupo_nombre}" ya existe, actualizando permisos...')
            
            # Limpiar permisos existentes
            grupo.permissions.clear()
            
            # Asignar permisos
            if config.get('permisos') == 'all':
                # Superusuario: todos los permisos
                all_permissions = Permission.objects.all()
                grupo.permissions.set(all_permissions)
                self.stdout.write(f'  → Asignados TODOS los permisos ({all_permissions.count()})')
            else:
                # Otros grupos: permisos específicos
                permisos_asignados = 0
                for modelo_nombre, acciones in config.get('modelos', {}).items():
                    for accion in acciones:
                        # Buscar el permiso
                        codename = f'{accion}_{modelo_nombre}'
                        try:
                            permiso = Permission.objects.get(codename=codename)
                            grupo.permissions.add(permiso)
                            permisos_asignados += 1
                        except Permission.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(f'  ⚠ Permiso no encontrado: {codename}')
                            )
                
                self.stdout.write(f'  → Asignados {permisos_asignados} permisos')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Grupos configurados exitosamente!'))
        self.stdout.write('\nGrupos creados:')
        for grupo in Group.objects.all():
            self.stdout.write(f'  • {grupo.name} ({grupo.permissions.count()} permisos)')
