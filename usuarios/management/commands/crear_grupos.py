from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Crea los grupos de usuarios con sus permisos correspondientes'

    def handle(self, *args, **kwargs):
        # Crear grupo Doctor
        doctor_group, created = Group.objects.get_or_create(name='Doctor')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Doctor" creado'))
            
            # Permisos para Doctor (acceso completo)
            permisos_doctor = Permission.objects.all()
            doctor_group.permissions.set(permisos_doctor)
            self.stdout.write(self.style.SUCCESS('  Permisos asignados a Doctor'))
        else:
            self.stdout.write(self.style.WARNING('- Grupo "Doctor" ya existe'))

        # Crear grupo Asistente
        asistente_group, created = Group.objects.get_or_create(name='Asistente')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Asistente" creado'))
            
            # Permisos para Asistente (puede ver y editar pacientes, citas, tratamientos)
            permisos_asistente = Permission.objects.filter(
                codename__in=[
                    # Pacientes
                    'view_paciente', 'add_paciente', 'change_paciente',
                    # Citas
                    'view_cita', 'add_cita', 'change_cita', 'delete_cita',
                    # Tratamientos
                    'view_tratamiento', 'add_tratamiento', 'change_tratamiento',
                    # Pagos
                    'view_pago', 'add_pago',
                    # Historias
                    'view_historiaclinica', 'add_historiaclinica', 'change_historiaclinica',
                    # Notas
                    'view_nota', 'add_nota', 'change_nota',
                ]
            )
            asistente_group.permissions.set(permisos_asistente)
            self.stdout.write(self.style.SUCCESS('  Permisos asignados a Asistente'))
        else:
            self.stdout.write(self.style.WARNING('- Grupo "Asistente" ya existe'))

        # Crear grupo Recepcionista
        recepcionista_group, created = Group.objects.get_or_create(name='Recepcionista')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Recepcionista" creado'))
            
            # Permisos para Recepcionista (solo citas y ver pacientes)
            permisos_recepcionista = Permission.objects.filter(
                codename__in=[
                    # Pacientes (solo ver y agregar)
                    'view_paciente', 'add_paciente',
                    # Citas (completo)
                    'view_cita', 'add_cita', 'change_cita', 'delete_cita',
                    # Pagos (solo ver)
                    'view_pago',
                ]
            )
            recepcionista_group.permissions.set(permisos_recepcionista)
            self.stdout.write(self.style.SUCCESS('  Permisos asignados a Recepcionista'))
        else:
            self.stdout.write(self.style.WARNING('- Grupo "Recepcionista" ya existe'))

        self.stdout.write(self.style.SUCCESS('\n✅ Grupos creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('Ahora puedes asignar usuarios a estos grupos desde el admin.'))
