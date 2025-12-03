# Sistema de Gestión para Consultorio Dental

Sistema completo de gestión para consultorios dentales desarrollado con Django.

## Características

- 👥 Gestión de pacientes
- 📅 Sistema de citas (integración con Google Calendar)
- 🦷 Odontograma interactivo
- 💰 Gestión de tratamientos y pagos
- 📝 Historias clínicas
- 🧸 Protocolo Niños (Evaluación funcional)
- 🌱 Programa Salud-Confort
- 📄 Exportación a PDF
- 📊 Dashboard con estadísticas
- 🔔 Notificaciones de cumpleaños y citas

## Requisitos

- Python 3.8+
- Django 5.2+
- SQLite (por defecto) o PostgreSQL

## Instalación

1. Clonar el repositorio:
```bash
git clone <tu-repositorio>
cd Consultorio_dental01
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Aplicar migraciones:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar servidor de desarrollo:
```bash
python manage.py runserver
```

## Configuración para Producción (PythonAnywhere)

1. Configurar `ALLOWED_HOSTS` en `settings.py`
2. Configurar `DEBUG = False`
3. Configurar archivos estáticos: `python manage.py collectstatic`
4. Configurar base de datos PostgreSQL (recomendado)

## Estructura del Proyecto

```
consultorio_dental/
├── pacientes/          # Gestión de pacientes
├── citas/              # Sistema de citas
├── tratamientos/       # Tratamientos y odontograma
├── historias/          # Historias clínicas
├── notas/              # Notas adicionales
├── protocolo_ninos/    # Evaluación funcional niños
├── programa_salud/     # Programa Salud-Confort
├── configuracion/      # Configuración del consultorio
└── dashboard/          # Dashboard principal
```

## Licencia

Todos los derechos reservados.

## Autor

Consultorio Dental - 2025
