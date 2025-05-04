from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Producto, ProductoImagen, Compra, DetalleCompra, Usuarios

@login_required
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    return render(request, 'users/admin_dashboard/inventory.html')

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
    return render(request, 'users/admin_dashboard/client_management.html')

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
    return render(request, 'users/admin_dashboard/orders_management.html')

# @login_required
# def admin_products(request):
#     """Listar todos los productos para el administrador"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     productos = Producto.objects.all().order_by('-created_at')
#     return render(request, 'users/admin_dashboard/products_list.html', {
#         'productos': productos
#     })

# @login_required
# def admin_add_product(request):
#     """Añadir un nuevo producto"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     # Esta vista necesitará un formulario, se implementará en forms/admin_forms.py
#     # Por ahora, solo mostrará la página del formulario
#     return render(request, 'users/admin_dashboard/add_product.html')

# @login_required
# def admin_edit_product(request, producto_id):
#     """Editar un producto existente"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     producto = get_object_or_404(Producto, id=producto_id)
#     # Implementación completa dependerá del formulario
#     return render(request, 'users/admin_dashboard/edit_product.html', {
#         'producto': producto
#     })

# @login_required
# def admin_delete_product(request, producto_id):
#     """Eliminar un producto"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     producto = get_object_or_404(Producto, id=producto_id)
#     if request.method == 'POST':
#         producto.delete()
#         messages.success(request, f'Producto "{producto.name}" eliminado correctamente.')
#         return redirect('admin_products')
    
#     return render(request, 'users/admin_dashboard/delete_product_confirm.html', {
#         'producto': producto
#     })

# @login_required
# def admin_orders(request):
#     """Listar todas las órdenes/compras"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     compras = Compra.objects.all().order_by('-fecha')
#     return render(request, 'users/admin_dashboard/orders_list.html', {
#         'compras': compras
#     })

# @login_required
# def admin_order_detail(request, compra_id):
#     """Ver detalles de una orden específica"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     compra = get_object_or_404(Compra, id=compra_id)
#     detalles = DetalleCompra.objects.filter(compra=compra)
    
#     return render(request, 'users/admin_dashboard/order_detail.html', {
#         'compra': compra,
#         'detalles': detalles
#     })

# @login_required
# def admin_update_order_status(request, compra_id):
#     """Actualizar el estado de una orden"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     compra = get_object_or_404(Compra, id=compra_id)
    
#     if request.method == 'POST':
#         nuevo_estado = request.POST.get('estado')
#         if nuevo_estado in [estado[0] for estado in Compra.ESTADO_CHOICES]:
#             compra.actualizar_estado(nuevo_estado)
#             messages.success(request, f'Estado de la orden #{compra.id} actualizado a "{nuevo_estado}".')
#         else:
#             messages.error(request, 'Estado inválido.')
#         return redirect('admin_order_detail', compra_id=compra.id)
    
#     return redirect('admin_orders')

# @login_required
# def admin_users(request):
#     """Listar todos los usuarios (solo para administradores)"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     usuarios = Usuarios.objects.all().order_by('-date_joined')
#     return render(request, 'users/admin_dashboard/users_list.html', {
#         'usuarios': usuarios
#     })

# @login_required
# def admin_user_detail(request, usuario_id):
#     """Ver detalles de un usuario específico"""
#     if request.user.rol != 'admin':
#         return redirect('client_dashboard')
    
#     usuario = get_object_or_404(Usuarios, id=usuario_id)
#     compras = Compra.objects.filter(usuario=usuario).order_by('-fecha')
    
#     return render(request, 'users/admin_dashboard/user_detail.html', {
#         'usuario': usuario,
#         'compras': compras
#     })