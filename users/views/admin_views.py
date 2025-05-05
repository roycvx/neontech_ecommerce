from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Producto, ProductoImagen, Compra, DetalleCompra, Usuarios
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

@login_required
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    # Obtener todos los productos para mostrarlos en la tabla
    productos = Producto.objects.all()
    
    return render(request, 'users/admin_dashboard/inventory.html', {'productos': productos})

@login_required
def inventory_form(request):
    """Formulario para agregar un nuevo producto al inventario"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')

    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('productName')
        description = request.POST.get('description')
        category = request.POST.get('type')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        
        # Validar que todos los campos requeridos estén presentes
        if not all([name, description, category, stock, price]):
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'users/admin_dashboard/inventory_form.html')
        
        try:
            # Crear un nuevo producto
            producto = Producto(
                name=name,
                description=description,
                category=category,
                stock=stock,
                price=price
            )
            
            # Crear estructura de carpetas para el producto
            # Convertir el nombre del producto para que sea válido como nombre de carpeta (reemplazar espacios por guiones)
            folder_name = name.replace(' ', '-').lower()
            
            # Determinar la categoría para la carpeta principal
            category_folder = 'laptops' if category == 'laptop' else 'celulares'
            
            # Construir la ruta para la carpeta del producto
            product_folder_path = os.path.join('productos', category_folder, folder_name)
            
            # Crear la ruta completa en el sistema de archivos
            full_product_path = os.path.join(settings.MEDIA_ROOT, product_folder_path)
            carrusel_path = os.path.join(full_product_path, 'carrusel')
            
            # Crear las carpetas si no existen
            os.makedirs(full_product_path, exist_ok=True)
            os.makedirs(carrusel_path, exist_ok=True)
            
            # Procesar la imagen principal del producto
            if 'productImage' in request.FILES:
                main_image = request.FILES['productImage']
                
                # Obtener la extensión del archivo
                _, extension = os.path.splitext(main_image.name)
                
                # Nombre de archivo para la imagen principal
                main_image_name = f"main{extension}"
                
                # Ruta relativa para guardar en la base de datos
                relative_image_path = os.path.join(product_folder_path, main_image_name)
                
                # Ruta completa para guardar físicamente el archivo
                full_image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
                
                # Guardar la imagen en el sistema de archivos
                with open(full_image_path, 'wb+') as destination:
                    for chunk in main_image.chunks():
                        destination.write(chunk)
                
                # Asignar la ruta relativa al modelo
                producto.img = relative_image_path
            
            # Guardar el producto en la base de datos
            producto.save()
            
            # Procesar imágenes adicionales si existen
            if 'additionalImages' in request.FILES:
                for i, img in enumerate(request.FILES.getlist('additionalImages')):
                    # Obtener la extensión del archivo
                    _, extension = os.path.splitext(img.name)
                    
                    # Nombre de archivo para la imagen adicional
                    additional_image_name = f"image_{i+1}{extension}"
                    
                    # Ruta relativa para guardar en la base de datos
                    relative_add_image_path = os.path.join(product_folder_path, 'carrusel', additional_image_name)
                    
                    # Ruta completa para guardar físicamente el archivo
                    full_add_image_path = os.path.join(settings.MEDIA_ROOT, relative_add_image_path)
                    
                    # Guardar la imagen en el sistema de archivos
                    with open(full_add_image_path, 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    
                    # Crear el registro en la base de datos
                    ProductoImagen.objects.create(
                        producto=producto,
                        imagen=relative_add_image_path
                    )
            
            messages.success(request, f"Producto '{name}' creado exitosamente")
            return redirect('inventory')
        
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {str(e)}")
    
    return render(request, 'users/admin_dashboard/inventory_form.html')

@login_required
def edit_product(request, product_id):
    """Vista para editar un producto existente"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    # Obtener el producto a editar
    producto = get_object_or_404(Producto, id=product_id)
    
    # Obtener las imágenes adicionales asociadas al producto
    imagenes_adicionales = ProductoImagen.objects.filter(producto=producto)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('productName')
        description = request.POST.get('description')
        category = request.POST.get('type')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        
        # Validar que todos los campos requeridos estén presentes
        if not all([name, description, category, stock, price]):
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'users/admin_dashboard/edit_product.html', {
                'producto': producto,
                'imagenes_adicionales': imagenes_adicionales
            })
        
        try:
            # Actualizar los datos básicos del producto
            producto.name = name
            producto.description = description
            producto.category = category
            producto.stock = stock
            producto.price = price
            
            # Verificar si se debe cambiar la imagen principal
            if 'productImage' in request.FILES:
                main_image = request.FILES['productImage']
                
                # Si ya existe una imagen, eliminarla del sistema de archivos
                if producto.img:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(producto.img))
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)
                
                # Definir la estructura de carpetas para el producto
                folder_name = name.replace(' ', '-').lower()
                category_folder = 'laptops' if category == 'laptop' else 'celulares'
                product_folder_path = os.path.join('productos', category_folder, folder_name)
                
                # Crear las carpetas si no existen
                full_product_path = os.path.join(settings.MEDIA_ROOT, product_folder_path)
                os.makedirs(full_product_path, exist_ok=True)
                
                # Obtener la extensión del archivo
                _, extension = os.path.splitext(main_image.name)
                
                # Nombre de archivo para la imagen principal
                main_image_name = f"main{extension}"
                
                # Ruta relativa para guardar en la base de datos
                relative_image_path = os.path.join(product_folder_path, main_image_name)
                
                # Ruta completa para guardar físicamente el archivo
                full_image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
                
                # Guardar la imagen en el sistema de archivos
                with open(full_image_path, 'wb+') as destination:
                    for chunk in main_image.chunks():
                        destination.write(chunk)
                
                # Asignar la ruta relativa al modelo
                producto.img = relative_image_path
            
            # Guardar los cambios en el producto
            producto.save()
            
            # Procesar imágenes adicionales si existen
            if 'additionalImages' in request.FILES:
                # Crear carpeta para imágenes de carrusel si no existe
                carrusel_folder_name = name.replace(' ', '-').lower()
                category_folder = 'laptops' if category == 'laptop' else 'celulares'
                product_folder_path = os.path.join('productos', category_folder, carrusel_folder_name)
                carrusel_path = os.path.join(product_folder_path, 'carrusel')
                full_carrusel_path = os.path.join(settings.MEDIA_ROOT, carrusel_path)
                os.makedirs(full_carrusel_path, exist_ok=True)
                
                for i, img in enumerate(request.FILES.getlist('additionalImages')):
                    # Obtener la extensión del archivo
                    _, extension = os.path.splitext(img.name)
                    
                    # Nombre de archivo para la imagen adicional
                    next_index = imagenes_adicionales.count() + i + 1
                    additional_image_name = f"image_{next_index}{extension}"
                    
                    # Ruta relativa para guardar en la base de datos
                    relative_add_image_path = os.path.join(carrusel_path, additional_image_name)
                    
                    # Ruta completa para guardar físicamente el archivo
                    full_add_image_path = os.path.join(settings.MEDIA_ROOT, relative_add_image_path)
                    
                    # Guardar la imagen en el sistema de archivos
                    with open(full_add_image_path, 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    
                    # Crear el registro en la base de datos
                    ProductoImagen.objects.create(
                        producto=producto,
                        imagen=relative_add_image_path
                    )
            
            # Manejar eliminación de imágenes adicionales
            imagenes_a_eliminar = request.POST.getlist('delete_images')
            for img_id in imagenes_a_eliminar:
                try:
                    imagen = ProductoImagen.objects.get(id=img_id)
                    # Eliminar archivo físico
                    if imagen.imagen:
                        img_path = os.path.join(settings.MEDIA_ROOT, str(imagen.imagen))
                        if os.path.isfile(img_path):
                            os.remove(img_path)
                    # Eliminar registro de la base de datos
                    imagen.delete()
                except ProductoImagen.DoesNotExist:
                    pass  # Ignorar si la imagen no existe
            
            messages.success(request, f"Producto '{name}' actualizado exitosamente")
            return redirect('inventory')
        
        except Exception as e:
            messages.error(request, f"Error al actualizar el producto: {str(e)}")
    
    # Si es GET o hubo un error en POST, mostrar el formulario con los datos actuales
    return render(request, 'users/admin_dashboard/inventory_form.html', {
        'producto': producto,
        'imagenes_adicionales': imagenes_adicionales
    })

@login_required
def delete_product(request, product_id):
    """Vista para eliminar un producto"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=product_id)
        
        try:
            # Guardar el nombre para el mensaje
            product_name = producto.name
            
            # Eliminar imágenes adicionales
            imagenes = ProductoImagen.objects.filter(producto=producto)
            for imagen in imagenes:
                if imagen.imagen:
                    # Eliminar archivo físico
                    img_path = os.path.join(settings.MEDIA_ROOT, str(imagen.imagen))
                    if os.path.isfile(img_path):
                        os.remove(img_path)
            
            # Eliminar imagen principal
            if producto.img:
                main_img_path = os.path.join(settings.MEDIA_ROOT, str(producto.img))
                if os.path.isfile(main_img_path):
                    os.remove(main_img_path)
                
                # Intentar eliminar directorios vacíos
                try:
                    # Obtener la ruta del directorio del producto
                    folder_name = producto.name.replace(' ', '-').lower()
                    category_folder = 'laptops' if producto.category == 'laptop' else 'celulares'
                    product_folder_path = os.path.join(settings.MEDIA_ROOT, 'productos', category_folder, folder_name)
                    
                    # Eliminar carpeta de carrusel si existe
                    carrusel_path = os.path.join(product_folder_path, 'carrusel')
                    if os.path.exists(carrusel_path):
                        if not os.listdir(carrusel_path):  # Verificar si está vacío
                            os.rmdir(carrusel_path)
                    
                    # Eliminar carpeta del producto si está vacía
                    if os.path.exists(product_folder_path):
                        if not os.listdir(product_folder_path):  # Verificar si está vacío
                            os.rmdir(product_folder_path)
                except Exception:
                    # Ignorar errores al eliminar directorios
                    pass
            
            # Eliminar el producto de la base de datos
            producto.delete()
            
            messages.success(request, f"Producto '{product_name}' eliminado exitosamente")
        except Exception as e:
            messages.error(request, f"Error al eliminar el producto: {str(e)}")
    
    return redirect('inventory')

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