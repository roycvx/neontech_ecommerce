from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms.auth_forms import LoginForm, RegisterForm
from ..models.user import Usuarios

def show_start_page(request):
    """Página de inicio de la aplicación"""
    return render(request, 'users/start_page.html')

def login_view(request):
    """Vista para iniciar sesión, redirige según el rol del usuario"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                # Buscar al usuario por correo electrónico
                user = Usuarios.objects.get(email=email)
                
                # Verificar la contraseña
                if user.check_password(password):  # Verificar si la contraseña es correcta
                    login(request, user)
                    # Redirigir según el rol
                    messages.success(request, '¡Has iniciado sesión correctamente!')
                    if user.rol == 'admin':
                        return redirect('inventory')
                    else:
                        return redirect('client_dashboard')
                else:
                    messages.error(request, 'Correo o contraseña inválidos.')
            except Usuarios.DoesNotExist:
                messages.error(request, 'Correo o contraseña inválidos.')

    else:
        form = LoginForm()
    
    return render(request, 'users/auth/login_page.html', {'form': form})

def register_view(request):
    """Vista para registrar nuevos usuarios (solo clientes)"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario registrado exitosamente!')
            return redirect('login')
        else:
            messages.error(request, 'Utilice credenciales más fuertes.')
    else:
        form = RegisterForm()
    
    return render(request, 'users/auth/register_page.html', {'form': form})

@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('start')