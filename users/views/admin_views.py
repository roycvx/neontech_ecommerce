from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Producto, ProductoImagen, Compra, DetalleCompra, Usuarios, Direccion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import shutil


@login_required
def admin_dashboard(request):
    """Panel principal del administrador que muestra el inventario de productos"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    productos = Producto.objects.all()
    # Obtener estadísticas de productos
    contexto = get_estadistics(request)  # Se obtiene el diccionario de datos
    
    # Pasar tanto el contexto como los productos al template
    return render(request, 'users/admin_dashboard/inventory.html', {
        'contexto': contexto,
        'productos': productos  # Agregar esta línea para pasar los productos al template
    })

@login_required
def clean_form(request):
    """Vista que redirecciona a un formulario vacío"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    return redirect('inventory_form')

@login_required
def inventory_form(request):
    """
    Controlador del formulario de creación de productos, 
    maneja la imagen principal y las imágenes adicionales.
    crea la estructura de carpetas necesarias.
    """
    if request.user.rol != 'admin':
        return redirect('client_dashboard')

    if request.method == 'POST':
        name = request.POST.get('productName')
        description = request.POST.get('description')
        category = request.POST.get('type')
        stock = request.POST.get('stock')
        price = request.POST.get('price', '0')
        price = price.replace(',', '.') 
        
        if not all([name, description, category, stock, price]):
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'users/admin_dashboard/inventory_form.html')
        
        try:
            # Crear registro del producto
            producto = Producto(
                name=name,
                description=description,
                category=category,
                stock=stock,
                price=price
            )
            
            # Configurar estructura de directorios
            folder_name = name.replace(' ', '-').lower()
            category_folder = 'laptops' if category == 'laptop' else 'celulares'
            product_folder_path = os.path.join('productos', category_folder, folder_name)
            full_product_path = os.path.join(settings.MEDIA_ROOT, product_folder_path)
            carrusel_path = os.path.join(full_product_path, 'carrusel')
            
            # Crear directorios
            os.makedirs(full_product_path, exist_ok=True)
            os.makedirs(carrusel_path, exist_ok=True)
            
            # Procesar imagen principal
            if 'productImage' in request.FILES:
                main_image = request.FILES['productImage']
                _, extension = os.path.splitext(main_image.name)
                main_image_name = f"main{extension}"
                relative_image_path = os.path.join(product_folder_path, main_image_name)
                full_image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
                
                with open(full_image_path, 'wb+') as destination:
                    for chunk in main_image.chunks():
                        destination.write(chunk)
                
                producto.img = relative_image_path
            
            producto.save()
            
            # Procesar imágenes del carrusel
            additional_files = request.FILES.getlist('additionalImages')

            if additional_files:
                for i, img in enumerate(additional_files):
                    _, extension = os.path.splitext(img.name)
                    additional_image_name = f"image_{i+1}{extension}"
                    relative_add_image_path = os.path.join(product_folder_path, 'carrusel', additional_image_name)
                    full_add_image_path = os.path.join(settings.MEDIA_ROOT, relative_add_image_path)
                    
                    with open(full_add_image_path, 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    
                    ProductoImagen.objects.create(
                        producto=producto,
                        imagen=relative_add_image_path
                    )
            
            messages.success(request, f"Producto '{name}' creado exitosamente")
            return redirect('inventory_form')  # Redirige a la lista de inventario
        
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    return render(request, 'users/admin_dashboard/inventory_form.html')

@login_required
def edit_product(request, product_id):
    """
    Edición de productos existentes. Muestra el formulario con datos del 
    producto seleccionado y actualiza la información en la base de datos.
    Maneja la imagen principal y las imágenes adicionales y crea las 
    carpetas necesarias, si estas cambian.
    """
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    producto = get_object_or_404(Producto, id=product_id)
    imagenes_adicionales = ProductoImagen.objects.filter(producto=producto)
    
    # Guardar datos originales para verificar cambios
    nombre_original = producto.name
    categoria_original = producto.category
    
    if request.method == 'POST':
        name = request.POST.get('productName')
        description = request.POST.get('description')
        category = request.POST.get('type')
        stock = request.POST.get('stock')
        price = request.POST.get('price', '0')
        price = price.replace(',', '.')
        
        if not all([name, description, category, stock, price]):
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'users/admin_dashboard/edit_product.html', {
                'producto': producto,
                'imagenes_adicionales': imagenes_adicionales
            })
        
        try:
            # Verificar cambios en nombre o categoría
            nombre_cambio = nombre_original != name
            categoria_cambio = categoria_original != category
            
            # Preparar rutas para nueva estructura
            folder_name = name.replace(' ', '-').lower()
            category_folder = 'laptops' if category == 'laptop' else 'celulares'
            product_folder_path = os.path.join('productos', category_folder, folder_name)
            carrusel_path = os.path.join(product_folder_path, 'carrusel')
            
            full_product_path = os.path.join(settings.MEDIA_ROOT, product_folder_path)
            full_carrusel_path = os.path.join(settings.MEDIA_ROOT, carrusel_path)
            
            # Reorganizar archivos si cambió nombre o categoría
            if (nombre_cambio or categoria_cambio) and producto.img:
                # Estructura de carpetas anterior
                old_folder_name = nombre_original.replace(' ', '-').lower()
                old_category_folder = 'laptops' if categoria_original == 'laptop' else 'celulares'
                old_product_folder_path = os.path.join('productos', old_category_folder, old_folder_name)
                old_carrusel_path = os.path.join(old_product_folder_path, 'carrusel')
                old_full_product_path = os.path.join(settings.MEDIA_ROOT, old_product_folder_path)
                
                # Crear nuevas carpetas solo si son diferentes
                if old_product_folder_path != product_folder_path:
                    os.makedirs(full_product_path, exist_ok=True)
                    os.makedirs(full_carrusel_path, exist_ok=True)
                    
                    # Mover imagen principal
                    if producto.img:
                        old_image_path = os.path.join(settings.MEDIA_ROOT, str(producto.img))
                        if os.path.isfile(old_image_path):
                            image_filename = os.path.basename(producto.img.name)
                            new_image_path = os.path.join(product_folder_path, image_filename)
                            full_new_image_path = os.path.join(settings.MEDIA_ROOT, new_image_path)
                            
                            os.makedirs(os.path.dirname(full_new_image_path), exist_ok=True)
                            shutil.copy2(old_image_path, full_new_image_path)
                            
                            producto.img = new_image_path
                    
                    # Mover imágenes del carrusel
                    for imagen in imagenes_adicionales:
                        if imagen.imagen:
                            old_add_image_path = os.path.join(settings.MEDIA_ROOT, str(imagen.imagen))
                            if os.path.isfile(old_add_image_path):
                                add_image_filename = os.path.basename(imagen.imagen.name)
                                new_add_image_path = os.path.join(carrusel_path, add_image_filename)
                                full_new_add_image_path = os.path.join(settings.MEDIA_ROOT, new_add_image_path)
                                
                                os.makedirs(os.path.dirname(full_new_add_image_path), exist_ok=True)
                                shutil.copy2(old_add_image_path, full_new_add_image_path)
                                
                                imagen.imagen = new_add_image_path
                                imagen.save()
                    
                    # Eliminar carpeta antigua
                    if os.path.exists(old_full_product_path):
                        shutil.rmtree(old_full_product_path)
            else:
                os.makedirs(full_product_path, exist_ok=True)
                os.makedirs(full_carrusel_path, exist_ok=True)
            
            # Actualizar datos básicos
            producto.name = name
            producto.description = description
            producto.category = category
            producto.stock = stock
            producto.price = price
            
            # Actualizar imagen principal si se proporciona nueva
            if 'productImage' in request.FILES:
                main_image = request.FILES['productImage']
                
                # Eliminar imagen anterior si existe
                if producto.img:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(producto.img))
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)
                
                _, extension = os.path.splitext(main_image.name)
                main_image_name = f"main{extension}"
                relative_image_path = os.path.join(product_folder_path, main_image_name)
                full_image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
                
                with open(full_image_path, 'wb+') as destination:
                    for chunk in main_image.chunks():
                        destination.write(chunk)
                
                producto.img = relative_image_path
            
            producto.save()
            
            # Procesar nuevas imágenes adicionales
            if 'additionalImages' in request.FILES:                
                for i, img in enumerate(request.FILES.getlist('additionalImages')):
                    _, extension = os.path.splitext(img.name)
                    next_index = imagenes_adicionales.count() + i + 1
                    additional_image_name = f"image_{next_index}{extension}"
                    relative_add_image_path = os.path.join(carrusel_path, additional_image_name)
                    full_add_image_path = os.path.join(settings.MEDIA_ROOT, relative_add_image_path)
                    
                    with open(full_add_image_path, 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    
                    ProductoImagen.objects.create(
                        producto=producto,
                        imagen=relative_add_image_path
                    )
            
            # Eliminar imágenes seleccionadas
            imagenes_a_eliminar = request.POST.getlist('delete_images')
            for img_id in imagenes_a_eliminar:
                try:
                    imagen = ProductoImagen.objects.get(id=img_id)
                    if imagen.imagen:
                        img_path = os.path.join(settings.MEDIA_ROOT, str(imagen.imagen))
                        if os.path.isfile(img_path):
                            os.remove(img_path)
                    imagen.delete()
                except ProductoImagen.DoesNotExist:
                    pass
            
            messages.success(request, f"Producto '{name}' actualizado exitosamente")
            return redirect('inventory')
        
        except Exception as e:
            messages.error(request, f"Error al actualizar el producto: {str(e)}")
    
    return render(request, 'users/admin_dashboard/inventory_form.html', {
        'producto': producto,
        'imagenes_adicionales': imagenes_adicionales
    })

@login_required
def delete_product(request, product_id):
    """Elimina un producto y todos sus archivos asociados."""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=product_id)
        
        try:
            product_name = producto.name
            
            # Eliminar imágenes adicionales
            imagenes = ProductoImagen.objects.filter(producto=producto)
            for imagen in imagenes:
                if imagen.imagen:
                    img_path = os.path.join(settings.MEDIA_ROOT, str(imagen.imagen))
                    if os.path.isfile(img_path):
                        os.remove(img_path)
            
            # Eliminar imagen principal
            if producto.img:
                main_img_path = os.path.join(settings.MEDIA_ROOT, str(producto.img))
                if os.path.isfile(main_img_path):
                    os.remove(main_img_path)
                
                # Limpiar directorios vacíos
                try:
                    folder_name = producto.name.replace(' ', '-').lower()
                    category_folder = 'laptops' if producto.category == 'laptop' else 'celulares'
                    product_folder_path = os.path.join(settings.MEDIA_ROOT, 'productos', category_folder, folder_name)
                    
                    carrusel_path = os.path.join(product_folder_path, 'carrusel')
                    if os.path.exists(carrusel_path) and not os.listdir(carrusel_path):
                        os.rmdir(carrusel_path)
                    
                    if os.path.exists(product_folder_path) and not os.listdir(product_folder_path):
                        os.rmdir(product_folder_path)
                except Exception:
                    pass
            
            # Eliminar registro en BD
            producto.delete()
            
            messages.success(request, f"Producto '{product_name}' eliminado exitosamente")
        except Exception as e:
            messages.error(request, f"Error al eliminar el producto: {str(e)}")
    
    return redirect('inventory')

@login_required
def admin_clients(request):
    """Muestra la lista de todos los clientes registrados."""
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
    """Formulario para agregar un nuevo cliente."""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')

    return render(request, 'users/admin_dashboard/client_form.html')

@login_required
def admin_orders(request):
    """Muestra la lista de todas las órdenes/compras."""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    contexto = get_estadistics(request) # Se obtiene el diccionario de datos
    compras = Compra.objects.all()

    for compra in compras:
        compra.formatted_total = f"{compra.total:.2f}".replace(',', '.') if compra.total else "0.00"

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
    ventas_brutas = f"{ventas_brutas:.2f}".replace(',', '.') 
           
    clientes = Usuarios.objects.all()
    total_de_clientes = 0
    for cliente in clientes:
        if cliente.rol != 'admin':
            total_de_clientes += 1

    pedidos_totales = Compra.objects.all().count
    
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