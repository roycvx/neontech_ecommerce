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

    for direccion in direcciones:

        for user in total_usuarios:

            if direccion.usuario_id == user['id']:
                user['telefono'] = direccion.telefono

    contexto = get_estadistics(request) # Se obtiene el diccionario de datos

    return render(request, 'users/admin_dashboard/client_management.html', {
        'contexto' : contexto,
        'usuarios' : total_usuarios
    })

@login_required
def delete_clients(request):

    id_usuario = request.POST.get('usuario_id')
    usuario = Usuarios.objects.filter(id = id_usuario)

    if usuario.delete():
        messages.success(request, '¡Usuario eliminado exitosamente!')
    else:
        messages.error(request, '¡Error al eliminar usuario!')

    return redirect('admin_clients')

@login_required
def update_clients(request):

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