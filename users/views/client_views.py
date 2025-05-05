from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from django.utils.timezone import now
from decimal import Decimal

from ..models import Producto, Carrito, Direccion, Tarjeta, Compra, DetalleCompra

# Constante para el cálculo de impuestos
ITBMS_RATE = Decimal('0.07')  # 7%

@login_required
def client_dashboard(request):
    """Dashboard principal del cliente"""
    carrito_items = Carrito.objects.filter(usuario=request.user)
    articulos = carrito_items.aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    return render(request, 'users/client_dashboard/client_dashboard.html', {
        'articulos': articulos
    })

def products_list(request, categoria):
    """Mostrar la lista de productos disponibles por categoría"""
    productos = Producto.objects.filter(category=categoria, stock__gt=0)

    carrito_items = Carrito.objects.filter(usuario=request.user)
    articulos = carrito_items.aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    if categoria == 'laptop':
        template = 'users/client_dashboard/search_laptops_page.html'
    else:  # categoria == 'celular'
        template = 'users/client_dashboard/search_phones_page.html'
    return render(request, template, {'productos': productos, 'articulos': articulos})

def show_detail_product(request, producto_id):
    """Mostrar los detalles del producto seleccionado"""
    producto = get_object_or_404(Producto, id=producto_id)
    imagenes = producto.galeria.all()  # gracias al related_name

    carrito = Carrito.objects.filter(usuario=request.user)
    articulos = carrito.aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    
    return render(request, 'users/client_dashboard/product_description.html', {
        'producto': producto,
        'imagenes': imagenes,
        'articulos': articulos
    })

@login_required
def show_shopping_cart(request):
    """Mostrar el carrito de compra"""
    carrito = Carrito.objects.filter(usuario=request.user)
    articulos = carrito.aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    subtotal = sum(Decimal(item.subtotal) for item in carrito)
    impuesto = subtotal * ITBMS_RATE
    total = subtotal + impuesto

    return render(request, 'users/client_dashboard/shopping_cart.html', {
        'carrito': carrito,
        'total': total,
        'subtotal': subtotal,
        'impuesto': impuesto,
        'articulos': articulos
    })

@login_required
def add_to_cart(request, producto_id):
    """Agregar un producto al carrito de compra"""
    if request.method == "POST":
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get("cantidad", 1))

        # Verificar que haya suficiente stock
        if producto.stock < cantidad:
            messages.error(request, "No hay suficiente stock disponible para este producto.")
            return redirect('detail_product', producto_id=producto_id)

        # Verifica si el producto ya está en el carrito del usuario
        item, created = Carrito.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={'cantidad': cantidad, 'subtotal': producto.price * cantidad}
        )

        if not created:
            if item.cantidad + cantidad > producto.stock:
                messages.error(request, "Has excedido el stock disponible para este producto.")
                return redirect('detail_product', producto_id=producto_id)
            item.cantidad += cantidad
            item.subtotal = item.producto.price * item.cantidad
            item.save()

        messages.success(request, "Producto añadido al carrito")

    return redirect('detail_product', producto_id=producto_id)

@login_required
def update_cart(request, producto_id):
    """Actualizar la cantidad de un producto en el carrito"""
    if request.method == 'POST':
        action = request.POST.get('action')
        item = get_object_or_404(Carrito, usuario=request.user, producto_id=producto_id)

        if action == 'increase':
            item.cantidad += 1
            item.subtotal = item.producto.price * item.cantidad  # Actualizar subtotal
        elif action == 'decrease' and item.cantidad > 1:
            item.cantidad -= 1
            item.subtotal = item.producto.price * item.cantidad  # Actualizar subtotal

        item.save()

    return redirect('shopping_cart')

@login_required
def remove_from_cart(request, producto_id):
    """Eliminar un producto del carrito"""
    item = get_object_or_404(Carrito, usuario=request.user, producto_id=producto_id)
    item.delete()
    return redirect('shopping_cart')

@login_required
def cart_payment(request):
    """Pantalla de pago del carrito de compra"""
    carrito = Carrito.objects.filter(usuario=request.user)

    subtotal = sum(Decimal(item.subtotal) for item in carrito)
    impuesto = subtotal * ITBMS_RATE
    total = subtotal + impuesto

    articulos = sum(item.cantidad for item in carrito)

    return render(request, 'users/client_dashboard/shopping_cart_payment.html', {
        'articulos': articulos,
        'total': total,
    })

def link_card(request):
    """Vincular tarjeta al usuario"""
    msg = "Verifique que sus crendenciales sean correctas."
    if request.method == "POST":
        serial_input = request.POST.get('serial')
        cvv_input = request.POST.get('cvv')
        fecha_input = request.POST.get('fecha')  # Esperando formato: YYYY-MM-DD
        tarjeta = Tarjeta.objects.filter(serial=serial_input).first()
        if tarjeta is None:
            messages.error(request, msg)
            return redirect('cart_payment_now')

        if tarjeta.cvv != cvv_input:
            messages.error(request, msg)
            return redirect('cart_payment_now')

        # Procesar la fecha ingresada desde el input (esperamos: YYYY-MM-DD)
        try:
            fecha_ingresada = datetime.strptime(fecha_input, "%Y-%m-%d").date()
            mes_input = fecha_ingresada.month
            anio_input = fecha_ingresada.year
        except ValueError:
            messages.error(request, msg)
            return redirect('cart_payment_now')

        # Verificar si la tarjeta ha expirado
        hoy = now().date()
        if anio_input < hoy.year or (anio_input == hoy.year and mes_input < hoy.month):
            messages.error(request, msg)
            return redirect('cart_payment_now')

        # Comparar con la fecha de la tarjeta registrada (solo mes y año)
        mes_real = tarjeta.fecha_expiracion.month
        anio_real = tarjeta.fecha_expiracion.year
        if (mes_input != mes_real) or (anio_input != anio_real):
            messages.error(request, msg)
            return redirect('cart_payment_now')

        # Asociar la tarjeta al usuario
        tarjeta.usuario = request.user
        tarjeta.save()
        messages.success(request, "¡Tarjeta asociada correctamente! Ahora puedes proceder con tu compra.")
        return redirect('cart_payment_now')

    return render(request, 'users/client_dashboard/shopping_cart.html')

@login_required
def process_payment(request):
    """Procesar el pago de la compra"""
    usuario = request.user

    try:
        tarjeta = Tarjeta.objects.get(usuario=usuario)
    except Tarjeta.DoesNotExist:
        messages.error(request, "Necesitas vincular una tarjeta antes de pagar.")
        return redirect('cart_payment_now')

    carrito_items = Carrito.objects.filter(usuario=usuario)
    if not carrito_items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart_payment_now')

    # Asegura que el total sea Decimal, no float
    total = sum(item.subtotal * (1 + ITBMS_RATE) for item in carrito_items)
    total = total.quantize(Decimal('0.01'))  # Redondea a 2 decimales

    # Verificar si el saldo es suficiente
    if tarjeta.saldo < total:
        messages.error(request, "Saldo insuficiente en tu tarjeta. Elimina productos del carrito.")
        return redirect('cart_payment_now')

    compra = Compra.objects.create(
        usuario=usuario,
        fecha=now(),
        total=total
    )

    for item in carrito_items:
        DetalleCompra.objects.create(
            compra=compra,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.price
        )
        item.producto.stock -= item.cantidad
        item.producto.save()

    # Descontar usando Decimal para evitar errores
    tarjeta.saldo = tarjeta.saldo - total
    tarjeta.save()

    carrito_items.delete()

    return redirect('successful_purchase')

def success_purchase(request):
    """Mostrar notificación de compra exitosa"""
    return render(request, 'users/client_dashboard/successful_purchase.html')

def register_address(request):
    """Guardar dirección de envío"""
    if request.method == 'POST':
        calle = request.POST.get('calle')
        telefono = request.POST.get('telefono')
        ciudad = request.POST.get('ciudad')
        provincia = request.POST.get('provincia')
        codigo_postal = request.POST.get('codigo_postal')

        if all([calle, telefono, ciudad, provincia, codigo_postal]):
            if not hasattr(request.user, 'direccion'):  # Verificar si ya tiene dirección
                Direccion.objects.create(
                    usuario=request.user,  # Añadido el usuario
                    calle=calle,
                    telefono=telefono,
                    ciudad=ciudad,
                    provincia=provincia,
                    codigo_postal=codigo_postal,
                )
                messages.success(request, '✅ Dirección guardada correctamente.')
            else:
                messages.error(request, '❌ Ya tienes una dirección registrada.')

        else:
            messages.error(request, '❌ Todos los campos son obligatorios.')

        return redirect('cart_payment_now')