from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Producto, ProductoImagen, Compra, DetalleCompra, Usuarios
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
    return render(request, 'users/admin_dashboard/inventory.html', {'productos': productos})

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
    return render(request, 'users/admin_dashboard/client_management.html')

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
    return render(request, 'users/admin_dashboard/orders_management.html')