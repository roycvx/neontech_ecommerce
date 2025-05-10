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
    
    productos = Producto.objects.all()
    return render(request, 'users/admin_dashboard/inventory.html', {'productos': productos})

@login_required
def inventory_form(request):
    """Formulario para agregar un nuevo producto al inventario"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')

    if request.method == 'POST':
        name = request.POST.get('productName')
        description = request.POST.get('description')
        category = request.POST.get('type')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        
        if not all([name, description, category, stock, price]):
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'users/admin_dashboard/inventory_form.html')
        
        try:
            # Crear producto
            producto = Producto(
                name=name,
                description=description,
                category=category,
                stock=stock,
                price=price
            )
            
            # Configurar rutas de carpetas
            folder_name = name.replace(' ', '-').lower()
            category_folder = 'laptops' if category == 'laptop' else 'celulares'
            product_folder_path = os.path.join('productos', category_folder, folder_name)
            full_product_path = os.path.join(settings.MEDIA_ROOT, product_folder_path)
            carrusel_path = os.path.join(full_product_path, 'carrusel')
            
            # Crear estructura de directorios
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
            
            # Procesar imágenes adicionales
            # Verificar si hay archivos adicionales
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
            return redirect('inventory_form')  # Redirigir a la lista de inventario en lugar del formulario
        
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {str(e)}")
            # Imprimir la excepción para depuración
            import traceback
            print(traceback.format_exc())
    
    return render(request, 'users/admin_dashboard/inventory_form.html')

@login_required
def edit_product(request, product_id):
    """Vista para editar un producto existente"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    
    producto = get_object_or_404(Producto, id=product_id)
    imagenes_adicionales = ProductoImagen.objects.filter(producto=producto)
    
    if request.method == 'POST':
        name = request.POST.get('productName')
        description = request.POST.get('description')
        category = request.POST.get('type')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        
        if not all([name, description, category, stock, price]):
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, 'users/admin_dashboard/edit_product.html', {
                'producto': producto,
                'imagenes_adicionales': imagenes_adicionales
            })
        
        try:
            # Actualizar datos básicos
            producto.name = name
            producto.description = description
            producto.category = category
            producto.stock = stock
            producto.price = price
            
            # Actualizar imagen principal
            if 'productImage' in request.FILES:
                main_image = request.FILES['productImage']
                
                if producto.img:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(producto.img))
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)
                
                folder_name = name.replace(' ', '-').lower()
                category_folder = 'laptops' if category == 'laptop' else 'celulares'
                product_folder_path = os.path.join('productos', category_folder, folder_name)
                
                full_product_path = os.path.join(settings.MEDIA_ROOT, product_folder_path)
                os.makedirs(full_product_path, exist_ok=True)
                
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
                carrusel_folder_name = name.replace(' ', '-').lower()
                category_folder = 'laptops' if category == 'laptop' else 'celulares'
                product_folder_path = os.path.join('productos', category_folder, carrusel_folder_name)
                carrusel_path = os.path.join(product_folder_path, 'carrusel')
                full_carrusel_path = os.path.join(settings.MEDIA_ROOT, carrusel_path)
                os.makedirs(full_carrusel_path, exist_ok=True)
                
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
    """Vista para eliminar un producto"""
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
            
            producto.delete()
            
            messages.success(request, f"Producto '{product_name}' eliminado exitosamente")
        except Exception as e:
            messages.error(request, f"Error al eliminar el producto: {str(e)}")
    
    return redirect('inventory')

@login_required
def admin_clients(request):
    """Lista de todos los clientes"""
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
    """Lista de todas las ordenes"""
    if request.user.rol != 'admin':
        return redirect('client_dashboard')
    return render(request, 'users/admin_dashboard/orders_management.html')