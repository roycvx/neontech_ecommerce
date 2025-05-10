/**
 * NeonTech Admin Panel - Main Scripts
 * Funcionalidades para el lado administrador de la aplicación NeonTech
 */

document.addEventListener('DOMContentLoaded', function() {
    // ==================== Sidebar Toggle ====================
    initSidebar();
    
    // ==================== File Upload & Image Preview ====================
    setupFileDropArea('mainImageDropArea', 'productImage', 'main-image-preview');
    setupFileDropArea('additionalImagesDropArea', 'additionalImages', 'additional-images-preview', true);
    initImagePreviews();
    
    // ==================== UI Enhancements ====================
    enhanceUI();
    
    // ==================== Form Reset Handlers ====================
    setupFormReset();
    
    // ==================== Existing Images Handlers ====================
    setupExistingImagesHandlers();

    // ==================== Form Submission Handlers ====================
    setupFormSubmission()
});

/**
 * Inicializa la funcionalidad del sidebar
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (!sidebarToggle || !sidebar || !sidebarOverlay) return;
    
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    });
    
    sidebarOverlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    });
    
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        }
    });
}

/**
 * Inicializa la vista previa de imágenes
 */
function initImagePreviews() {
    // Vista previa para la imagen principal
    const mainImageInput = document.getElementById('productImage');
    if (mainImageInput) {
        mainImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                let previewContainer = document.querySelector('.main-image-preview');
                if (!previewContainer) return;
                
                previewContainer.classList.remove('hidden');
                
                // Limpiar vista previa anterior
                const imgContainer = previewContainer.querySelector('.preview-container');
                if (!imgContainer) return;
                imgContainer.innerHTML = '';
                
                // Crear el contenedor para la imagen
                const imagePreview = document.createElement('div');
                imagePreview.className = 'preview-item relative w-64 h-48 overflow-hidden rounded-lg border border-sky-500/30 group';
                
                // Crear la imagen de vista previa
                const previewImage = document.createElement('img');
                previewImage.className = 'w-full h-full object-contain';
                
                // Tooltip con nombre de archivo
                const tooltip = document.createElement('div');
                tooltip.className = 'image-tooltip';
                tooltip.textContent = this.files[0].name;
                
                // Botón para eliminar la imagen
                const removeBtn = document.createElement('button');
                removeBtn.className = 'preview-actions absolute top-2 right-2 bg-red-500/80 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    // Reiniciar el input file
                    mainImageInput.value = '';
                    // Ocultar la vista previa
                    previewContainer.classList.add('hidden');
                });
                
                // Leer el archivo y mostrar la vista previa
                const reader = new FileReader();
                reader.onload = e => previewImage.src = e.target.result;
                reader.readAsDataURL(this.files[0]);
                
                // Agregar elementos al DOM
                imagePreview.appendChild(previewImage);
                imagePreview.appendChild(tooltip);
                imagePreview.appendChild(removeBtn);
                imgContainer.appendChild(imagePreview);
            }
        });
    }
    
    // Vista previa para imágenes adicionales
    const additionalImagesInput = document.getElementById('additionalImages');
    if (additionalImagesInput) {
        // Crear un objeto para mantener todas las imágenes seleccionadas
        let selectedFiles = new DataTransfer();
        
        additionalImagesInput.addEventListener('change', function() {
            console.log("Archivos seleccionados:", this.files.length);
            if (!this.files || this.files.length === 0) return;
            
            // Buscar o mostrar el contenedor de vista previa
            let previewContainer = document.querySelector('.additional-images-preview');
            if (!previewContainer) return;
            
            previewContainer.classList.remove('hidden');
            
            // Obtener el grid donde se mostrarán las vistas previas
            const previewGrid = previewContainer.querySelector('.preview-grid');
            if (!previewGrid) return;
            
            selectedFiles = new DataTransfer();

            // Agregar los nuevos archivos seleccionados al DataTransfer que mantiene todas las selecciones
            for (let i = 0; i < this.files.length; i++) {
                selectedFiles.items.add(this.files[i]);
            }
            
            // Actualizar el input con todos los archivos acumulados
            this.files = selectedFiles.files;
            
            // Limpiar la vista previa actual para actualizarla con todas las imágenes
            previewGrid.innerHTML = '';
            
            // Procesar cada archivo acumulado
            for (let index = 0; index < selectedFiles.files.length; index++) {
                const file = selectedFiles.files[index];
                
                // Crear el contenedor para la imagen
                const imagePreview = document.createElement('div');
                imagePreview.className = 'preview-item relative aspect-square overflow-hidden rounded-lg border border-sky-500/30 group';
                imagePreview.dataset.index = index;
                
                // Crear la imagen de vista previa
                const previewImage = document.createElement('img');
                previewImage.className = 'w-full h-full object-cover';
                
                // Tooltip con nombre de archivo
                const tooltip = document.createElement('div');
                tooltip.className = 'image-tooltip';
                tooltip.textContent = file.name;
                
                // Botón para eliminar la imagen
                const removeBtn = document.createElement('button');
                removeBtn.className = 'preview-actions absolute top-1 right-1 bg-red-500/80 hover:bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Eliminar la imagen de la lista mantenida
                    const newSelectedFiles = new DataTransfer();
                    
                    for (let i = 0; i < selectedFiles.files.length; i++) {
                        if (i !== parseInt(imagePreview.dataset.index)) {
                            newSelectedFiles.items.add(selectedFiles.files[i]);
                        }
                    }
                    
                    // Actualizar la colección de archivos
                    selectedFiles = newSelectedFiles;
                    additionalImagesInput.files = selectedFiles.files;
                    
                    // Eliminar la vista previa
                    imagePreview.remove();
                    
                    // Actualizar el contador
                    const imageCountElem = previewContainer.querySelector('p + p');
                    if (imageCountElem) {
                        imageCountElem.textContent = `${additionalImagesInput.files.length} imagen(es) seleccionada(s)`;
                    }
                    
                    // Ocultar el contenedor si no hay imágenes
                    if (additionalImagesInput.files.length === 0) {
                        previewContainer.classList.add('hidden');
                    }
                    
                    // Reasignar índices a los elementos restantes
                    const remainingPreviews = previewGrid.querySelectorAll('.preview-item');
                    remainingPreviews.forEach((item, i) => {
                        item.dataset.index = i;
                    });
                });
                
                // Leer el archivo y mostrar la vista previa
                const reader = new FileReader();
                reader.onload = e => previewImage.src = e.target.result;
                reader.readAsDataURL(file);
                
                // Agregar elementos al DOM
                imagePreview.appendChild(previewImage);
                imagePreview.appendChild(tooltip);
                imagePreview.appendChild(removeBtn);
                previewGrid.appendChild(imagePreview);
            }
            
            // Crear o actualizar contador de imágenes
            let imageCount = previewContainer.querySelector('p + p');
            if (imageCount) {
                imageCount.textContent = `${selectedFiles.files.length} imagen(es) seleccionada(s)`;
            } else {
                imageCount = document.createElement('p');
                imageCount.className = 'text-xs text-gray-400 mt-1';
                imageCount.textContent = `${selectedFiles.files.length} imagen(es) seleccionada(s)`;
                previewContainer.querySelector('p').after(imageCount);
            }
        });
    }
}

/**
 * Configura el área de drag and drop para carga de archivos
 * @param {string} dropAreaId - ID del área donde se puede soltar archivos
 * @param {string} fileInputId - ID del input file asociado
 * @param {string} previewClass - Clase del contenedor de vista previa
 * @param {boolean} isMultiple - Si permite múltiples archivos
 */
function setupFileDropArea(dropAreaId, fileInputId, previewClass, isMultiple = false) {
    const dropArea = document.getElementById(dropAreaId);
    const fileInput = document.getElementById(fileInputId);
    
    if (!dropArea || !fileInput) return;
    
    // Asegurarse de que el atributo "multiple" esté correctamente configurado
    if (isMultiple) {
        fileInput.setAttribute('multiple', 'multiple');
    } else {
        fileInput.removeAttribute('multiple');
    }
    
    // Eventos de arrastrado
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    // Efectos visuales durante el arrastre
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('drag-over'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('drag-over'), false);
    });
    
    // Manejar el drop
    dropArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (isMultiple) {
            // Para múltiples archivos, creamos un DataTransfer para acumular todos los archivos
            const dataTransfer = new DataTransfer();
            
            // Primero, conservar los archivos que ya estaban seleccionados
            if (fileInput.files && fileInput.files.length > 0) {
                for (let i = 0; i < fileInput.files.length; i++) {
                    dataTransfer.items.add(fileInput.files[i]);
                }
            }
            
            // Luego, añadir los nuevos archivos soltados
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            
            // Asignar todos los archivos al input
            fileInput.files = dataTransfer.files;
        } else if (files.length > 0) {
            // Para un solo archivo, simplemente tomamos el primero
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            fileInput.files = dataTransfer.files;
        }
        
        // Disparar el evento change para activar la previsualización
        fileInput.dispatchEvent(new Event('change'));
    });
    
    // Permitir clic en el área de drop
    dropArea.addEventListener('click', () => fileInput.click());
}

/**
 * Mejora la UI con efectos visuales
 */
function enhanceUI() {
    // Efecto de ondulación para botones
    const buttons = document.querySelectorAll('button, .glow-button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;
            
            const ripple = document.createElement('span');
            ripple.className = 'absolute bg-white opacity-30 rounded-full';
            ripple.style.width = ripple.style.height = '100px';
            ripple.style.left = `${x - 50}px`;
            ripple.style.top = `${y - 50}px`;
            ripple.style.transform = 'scale(0)';
            ripple.style.position = 'absolute';
            ripple.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.style.transform = 'scale(4)';
                ripple.style.opacity = '0';
                setTimeout(() => ripple.remove(), 600);
            }, 10);
        });
    });
    
    // Efecto de focus para inputs
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

/**
 * Configura el reseteo del formulario
 */
function setupFormReset() {
    const productForm = document.getElementById('productForm');
    if (!productForm) return;
    
    productForm.addEventListener('reset', function() {
        // Ocultar todas las vistas previas
        const previewContainers = document.querySelectorAll('.main-image-preview, .additional-images-preview');
        previewContainers.forEach(container => container.classList.add('hidden'));
        
        // Limpiar los contenedores de vista previa
        const previewGrids = document.querySelectorAll('.preview-container, .preview-grid');
        previewGrids.forEach(grid => grid.innerHTML = '');
        
        // Eliminar los contadores de imágenes
        const counters = document.querySelectorAll('.additional-images-preview p + p');
        counters.forEach(counter => counter.remove());
        
        // Resetear los inputs file
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.value = '';
            // Esto disparará el evento change que limpiará la colección de archivos mantenida
            input.dispatchEvent(new Event('change'));
        });
        
        // CORRECCIÓN: Desmarcar checkboxes de eliminación de imágenes existentes
        const deleteCheckboxes = document.querySelectorAll('input[name="delete_images"]');
        deleteCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
            // Disparar el evento change para restaurar la apariencia
            checkbox.dispatchEvent(new Event('change'));
        });
    });
}

/**
 * Configura los manejadores para las imágenes existentes
 */
function setupExistingImagesHandlers() {
    const existingImagesContainer = document.getElementById('existingImagesContainer');
    if (!existingImagesContainer) return;
    
    const deleteCheckboxes = existingImagesContainer.querySelectorAll('input[name="delete_images"]');
    
    deleteCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const imageContainer = this.closest('.existing-image-item');
            if (!imageContainer) return;
            
            const img = imageContainer.querySelector('img');
            const overlay = imageContainer.querySelector('.delete-overlay');
            
            if (this.checked) {
                img.classList.add('opacity-50');
                overlay.classList.remove('opacity-0');
                overlay.classList.add('opacity-100');
            } else {
                img.classList.remove('opacity-50');
                overlay.classList.add('opacity-0');
                overlay.classList.remove('opacity-100');
            }
        });
    });
}
 /**
 * Configura el envío del formulario
 */
function setupFormSubmission() {
    const form = document.getElementById('productForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        // Verificar si hay imágenes adicionales seleccionadas
        const additionalImages = document.getElementById('additionalImages');
        if (additionalImages && additionalImages.files.length > 0) {
            console.log(`Se enviarán ${additionalImages.files.length} imágenes adicionales`);
        }
        
        // Agregar un log para confirmar el envío
        console.log('Enviando formulario con los siguientes datos:');
        const formData = new FormData(form);
        
        // Verificar si formData contiene las imágenes adicionales
        if (formData.getAll('additionalImages').length > 0) {
            console.log(`FormData contiene ${formData.getAll('additionalImages').length} imágenes adicionales`);
        } else {
            console.log('FormData no contiene imágenes adicionales');
        }
    });
}

/**
 * Carga los datos de un producto en el formulario (para edición)
 * @param {Object} producto - Datos del producto a cargar
 */
function loadProductData(producto) {
    if (!producto) return;
    
    // Cargar datos básicos del producto
    const fields = {
        'productId': producto.id,
        'productName': producto.name,
        'description': producto.description,
        'type': producto.category,
        'stock': producto.stock,
        'price': producto.price
    };
    
    // Establecer valores en los campos
    Object.entries(fields).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            // Asegurarse de que el valor sea una cadena para evitar problemas con números
            element.value = value.toString();
            console.log(`Campo ${id} actualizado con valor: ${value}`);
        }
    });
    
    // Si la imagen principal existe, mostrarla en la vista previa
    if (producto.img) {
        const mainImagePreview = document.querySelector('.main-image-preview');
        if (!mainImagePreview) return;
        
        mainImagePreview.classList.remove('hidden');
        
        const previewContainer = mainImagePreview.querySelector('.preview-container');
        if (!previewContainer) return;
        
        // Limpiar contenedor antes de agregar imagen
        previewContainer.innerHTML = '';
        
        // Crear elemento para la vista previa
        const imagePreview = document.createElement('div');
        imagePreview.className = 'preview-item relative w-64 h-48 overflow-hidden rounded-lg border border-sky-500/30 group';
        
        const previewImage = document.createElement('img');
        previewImage.className = 'w-full h-full object-contain';
        previewImage.src = producto.img;
        
        const existingLabel = document.createElement('div');
        existingLabel.className = 'absolute top-2 left-2 bg-sky-500/80 text-white text-xs px-2 py-1 rounded-md';
        existingLabel.textContent = 'Imagen actual';
        
        imagePreview.appendChild(previewImage);
        imagePreview.appendChild(existingLabel);
        previewContainer.appendChild(imagePreview);
    }
    
    // Configurar los manejadores para las imágenes existentes
    setupExistingImagesHandlers();



}