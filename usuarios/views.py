# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserCreateForm, UserEditForm
from .models import PerfilUsuario
from auditoria.utils import registrar_log

def es_admin_o_super(user):
    """Verifica si el usuario es administrador o superusuario"""
    return user.is_superuser or user.groups.filter(name='Administrador').exists()

# ===== AUTENTICACIÓN =====

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Registrar en auditoría
            registrar_log(
                usuario=user,
                accion='LOGIN',
                modelo='Usuario',
                objeto_id=user.id,
                objeto_repr=user.get_full_name() or user.username,
                detalles=f'Usuario inició sesión: {user.username}',
                request=request
            )
            
            messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    # Registrar en auditoría ANTES de cerrar sesión
    if request.user.is_authenticated:
        registrar_log(
            usuario=request.user,
            accion='LOGOUT',
            modelo='Usuario',
            objeto_id=request.user.id,
            objeto_repr=request.user.get_full_name() or request.user.username,
            detalles=f'Usuario cerró sesión: {request.user.username}',
            request=request
        )
    
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('usuarios:login')

# ===== GESTIÓN DE USUARIOS =====

@login_required
@user_passes_test(es_admin_o_super)
def lista_usuarios(request):
    usuarios = User.objects.all().select_related('perfil').prefetch_related('groups')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin_o_super)
def crear_usuario(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente')
            return redirect('usuarios:lista')
    else:
        form = UserCreateForm()
    
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

@login_required
@user_passes_test(es_admin_o_super)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente')
            return redirect('usuarios:lista')
    else:
        form = UserEditForm(instance=usuario)
    
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
@user_passes_test(es_admin_o_super)
def toggle_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    
    if usuario.is_superuser and not request.user.is_superuser:
        messages.error(request, 'No puedes desactivar a un superusuario')
        return redirect('usuarios:lista')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'Usuario {usuario.username} {estado} exitosamente')
    return redirect('usuarios:lista')