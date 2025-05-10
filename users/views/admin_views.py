from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Producto, ProductoImagen, Compra, DetalleCompra, Usuarios, Direccion

@login_required
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    contexto = get_estadistics(request) # Se obtiene el diccionario de datos
    
    return render(request, 'users/admin_dashboard/inventory.html', {
        'contexto' : contexto
    })

@login_required
def inventory_form(request):
    """Formulario para agregar un nuevo producto al inventario"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')

    return render(request, 'users/admin_dashboard/inventory_form.html')

@login_required
def admin_clients(request):
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    usuarios = Usuarios.objects.all()
    direcciones = Direccion.objects.all()

    datos = get_data_users(usuarios)
    datos = associate_phon_number_to_users(datos, direcciones)

    contexto = get_estadistics(request) # Se obtiene el diccionario de datos

    return render(request, 'users/admin_dashboard/client_management.html', {
        'contexto' : contexto,
        'usuarios': datos
    })

@login_required
def delete_clients(request):
    id_usuario = request.POST.get('usuario_id')  # ID del usuario a eliminar
    rol = request.POST.get('usuario_rol')        # Rol del usuario a eliminar

    # Obtener el ID del usuario logueado desde la cookie
    logged_user_id = request.user.id

    try:
        usuario = Usuarios.objects.get(id=id_usuario)
    except Usuarios.DoesNotExist:
        messages.error(request, '¡Usuario no encontrado!')
        return redirect('admin_clients')

    # Prevenir auto-eliminación si el logueado es admin y quiere borrarse a sí mismo
    if rol == 'admin' and str(id_usuario) == str(logged_user_id):
        messages.error(request, '¡No puedes eliminar tu propio usuario admin!')
    else:
        usuario.delete()
        messages.success(request, '¡Usuario eliminado exitosamente!')

    return redirect('admin_clients')

@login_required
def update_data_users(request, usuario_id, usuario_telefono):

    existe_usuario = Usuarios.objects.filter(id=usuario_id).exists()
    
    if existe_usuario:
        users = Usuarios.objects.get(id=usuario_id)

    primer_nombre = users.first_name
    primer_apellido = users.last_name
    email = users.email
    telefono = usuario_telefono
    nombre_usuario = users.username
    rol = users.rol
    esta_activo = users.is_active

    return render(request, 'users/admin_dashboard/client_form.html', {
        'usuario_id': usuario_id,
        'primer_nombre': primer_nombre,
        'primer_apellido': primer_apellido,
        'email': email,
        'telefono': telefono,
        'nombre_usuario': nombre_usuario,
        'rol': rol,
        'esta_activo': esta_activo,
        'existe_usuario': existe_usuario
      
    })

@login_required
def create_and_update_users(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('id_usuario')
        contrasena = request.POST.get('password')
        print(contrasena)
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Validación de email duplicado
        if Usuarios.objects.filter(email=email).exists():
            if not usuario_id:
                messages.error(request, 'Ese correo electrónico ya está en uso por otro cliente.')
                return redirect('client_form')
            try:
                usuario_existente = Usuarios.objects.get(email=email)
                if str(usuario_existente.id) != usuario_id:
                    messages.error(request, 'Ese correo electrónico ya está en uso por otro cliente.')
                    return redirect('client_form')
            except Usuarios.DoesNotExist:
                pass  # Por si acaso

        # CREACIÓN o ACTUALIZACIÓN
        if usuario_id and usuario_id.strip() != '':
            try:
                usuario = Usuarios.objects.get(id=int(usuario_id))
            except (Usuarios.DoesNotExist, ValueError):
                messages.error(request, 'El cliente especificado no existe o el ID es inválido.')
                return redirect('client_form')

            # Validar si el username se está cambiando y si ya está en uso
            if usuario.username != username and Usuarios.objects.filter(username=username).exists():
                messages.error(request, 'Ese nombre de usuario ya está en uso por otro cliente.')
                return redirect('client_form')

            mensaje = '¡Datos de cliente actualizados correctamente!'
        else:
            # Validar si el username ya está en uso
            if Usuarios.objects.filter(username=username).exists():
                messages.error(request, 'Ese nombre de usuario ya está en uso.')
                return redirect('client_form')

            usuario = Usuarios()
            mensaje = '¡Cliente guardado correctamente!'

        # Asignación de campos
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = email
        usuario.telefono = request.POST.get('phone_number')
        usuario.username = username
        usuario.rol = request.POST.get('rol')
        usuario.is_active = request.POST.get('is_active')

        # Cambiar contraseña solo si se ha proporcionado
        if contrasena:
            usuario.set_password(contrasena)

        usuario.save()
        messages.success(request, mensaje)
        return redirect('admin_clients')

    # Si no es POST, redirigir al formulario
    return redirect('client_form')


@login_required
def client_form(request):
    """Formulario para agregar un nuevo cliente"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')

    return render(request, 'users/admin_dashboard/client_form.html')

@login_required
def admin_orders(request):
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    contexto = get_estadistics(request) # Se obtiene el diccionario de datos
    compras = Compra.objects.all()

    return render(request, 'users/admin_dashboard/orders_management.html', {
        'contexto' : contexto,
        'compras' : compras,
    })

@login_required
def update_state(request, compra_id):
    if request.method == 'POST':
        compra = get_object_or_404(Compra, id=compra_id)
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Compra.ESTADO_CHOICES).keys():
            compra.estado = nuevo_estado
            compra.save()
            messages.success(request,'¡Estado de la compra actualizado con éxito!')
        else:
            messages.error(request,'¡Estado de la compra no se actualizo correctamente!')
    return redirect('admin_orders')  # Redirige de nuevo a la lista de órdenes

@login_required
def get_estadistics(request):
    """ Esta función obtiene algunas informaciones sobre operaciones"""
    compras = Compra.objects.all()
    ventas_brutas = 0
    for venta in compras:
        ventas_brutas += venta.total
           
    clientes = Usuarios.objects.all()
    total_de_clientes = 0
    for cliente in clientes:
        if cliente.rol != 'admin':
            total_de_clientes += 1

    pedidos_totales = DetalleCompra.objects.all().count
    
    datos = {
        'ventas_brutas': ventas_brutas,
        'total_de_clientes':total_de_clientes,
        'pedidos_totales': pedidos_totales
    }

    return datos


def get_data_users(usuarios):
        
    total_usuarios = []
    for usuario in usuarios:

        datos_usuarios = {
            'id': usuario.id,
            'first_name': usuario.first_name.capitalize(),
            'last_name': usuario.last_name.capitalize(),
            'email': usuario.email,
            'telefono': 'no capturado',
            'rol': usuario.rol
        }

        total_usuarios.append(datos_usuarios)
    
    return total_usuarios

def associate_phon_number_to_users(datos, direcciones):

    for direccion in direcciones:

        for user in datos:

            if direccion.usuario_id == user['id']:
                user['telefono'] = direccion.telefono
    return  datos