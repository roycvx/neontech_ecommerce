from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .forms import LoginForm, registerForm
from .models import Producto, Carrito, DetalleCompra, Compra
from decimal import Decimal

ITBMS_RATE = Decimal('0.07')  # 7%

# Página de inicio
def show_start_page(request):
    return render(request, 'users/start_page.html')

# Registro
def register_view(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario registrado exitosamente!')
            return redirect('login')
        else:
            messages.error(request, 'Hubo un error en el formulario.')
    else:
        form = registerForm()
    
    return render(request, 'users/register_page.html', {
        'form': form
    })

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Si el usuario es un admin, redirigir al dashboard admin
                if user.rol == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('client_dashboard')
            else:
                messages.error(request, 'Correo o contraseña inválidos.')
    else:
        form = LoginForm()

    return render(request, 'users/login_page.html', {'form': form})

# Dashboard (Admin)
@login_required
def admin_dashboard(request):
    # Redirigir si el usuario no es admin
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    return render(request, 'users/admin_dashboard/admin_dashboard.html')

# Dashboard (cliente)
from django.db.models import Sum

@login_required
def client_dashboard(request):
    carrito_items = Carrito.objects.filter(usuario=request.user)
    articulos = carrito_items.aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    return render(request, 'users/client_dashboard/client_dashboard.html', {
        'articulos': articulos
    })

# Mostrar la lista de productos disponibles
def products_list(request, categoria):
    productos = Producto.objects.filter(category=categoria, stock__gt=0)

    carrito_items = Carrito.objects.filter(usuario=request.user)
    articulos = carrito_items.aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    if categoria == 'laptop':
        template = 'users/client_dashboard/search_laptops_page.html'
    else:  # categoria == 'celular'
        template = 'users/client_dashboard/search_phones_page.html'
    return render(request, template, {'productos': productos, 'articulos': articulos})

# Mostrar los detalles del producto seleccionado
def show_detail_product(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    imagenes = producto.galeria.all()  # gracias al related_name

    carrito = Carrito.objects.filter(usuario=request.user)
    articulos = carrito.aggregate(Sum('cantidad'))['cantidad__sum'] or 0
    
    return render(request, 'users/client_dashboard/product_description.html', {
        'producto': producto,
        'imagenes': imagenes,
        'articulos': articulos
    })

# Mostrar el carrito de compra 
@login_required
def show_shopping_cart(request):
    carrito = Carrito.objects.filter(usuario=request.user)
    articulos = carrito.aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    subtotal = sum(Decimal(item.subtotal) for item in carrito)
    impuesto = subtotal * Decimal('0.07')
    total = subtotal + impuesto

    return render(request, 'users/client_dashboard/shopping_cart.html', {
        'carrito': carrito,
        'total': total,
        'subtotal': subtotal,
        'impuesto': impuesto,
        'articulos': articulos
    })

# Agregar un producto al carrito de compra
@login_required
def add_to_cart(request, producto_id):
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


# Actualizar el carrito de compra
@login_required
def update_cart(request, producto_id):
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

# Eliminar el carrito de compra
@login_required
def remove_from_cart(request, producto_id):
    item = get_object_or_404(Carrito, usuario=request.user, producto_id=producto_id)
    item.delete()
    return redirect('shopping_cart')

# Mostrar la pantalla de pag del carrito de compra
@login_required
def cart_payment(request):
    carrito = Carrito.objects.filter(usuario=request.user)

    subtotal = sum(Decimal(item.subtotal) for item in carrito)
    impuesto = subtotal * Decimal('0.07')
    total = subtotal + impuesto

    articulos = sum(item.cantidad for item in carrito)  # Aquí se suma la cantidad de todos los productos

    return render(request, 'users/client_dashboard/shopping_cart_payment.html', {
        'articulos': articulos,
        'total': total,
    })

# TEMA DE PAGOS
from datetime import datetime
from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Tarjeta

# Vincular tarjeta
def link_card(request):
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


# PROCESAR PAGO
from django.utils.timezone import now

@login_required
def process_payment(request):
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

    # ✅ Asegura que el total sea Decimal, no float
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

    # ✅ Descontar usando Decimal para evitar errores
    tarjeta.saldo = tarjeta.saldo - total
    tarjeta.save()

    carrito_items.delete()

    return redirect('successful_purchase')

# Mostrar notifiacion de compra exitosa
def success_purchase(request):
    return render(request, 'users/client_dashboard/successful_purchase.html')