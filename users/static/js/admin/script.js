 // Toggle Sidebar functionality
 document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    // Toggle sidebar when clicking the button
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    });
    
    // Close sidebar when clicking the overlay
    sidebarOverlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    });
    
    // Close sidebar on window resize if screen becomes larger
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        }
    });
});

// Mejorado script.js para gestión de imágenes y formulario de productos
document.addEventListener('DOMContentLoaded', function() {
    // Función para manejar el drag and drop en áreas de carga de archivos
    function setupFileDropArea(dropAreaId, fileInputId, previewClass, isMultiple = false) {
        const dropArea = document.getElementById(dropAreaId);
        const fileInput = document.getElementById(fileInputId);
        
        if (!dropArea || !fileInput) return;
        
        // Eventos de arrastrado
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Efectos visuales durante el arrastre
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropArea.classList.add('drag-over');
        }
        
        function unhighlight() {
            dropArea.classList.remove('drag-over');
        }
        
        // Manejar el drop
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (isMultiple) {
                fileInput.files = files;
            } else if (files.length > 0) {
                // Para input de archivo único, solo usamos el primer archivo
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(files[0]);
                fileInput.files = dataTransfer.files;
            }
            
            // Disparar el evento change para activar la previsualización
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
        
        // También permitir clic en el área de drop
        dropArea.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // Configurar áreas de drop para imagen principal y adicionales
    setupFileDropArea('mainImageDropArea', 'productImage', 'main-image-preview');
    setupFileDropArea('additionalImagesDropArea', 'additionalImages', 'additional-images-preview', true);
    
    // Vista previa para la imagen principal
    const mainImageInput = document.getElementById('productImage');
    if (mainImageInput) {
        mainImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // Buscar o mostrar el contenedor de vista previa
                let previewContainer = document.querySelector('.main-image-preview');
                if (previewContainer) {
                    previewContainer.classList.remove('hidden');
                    
                    // Limpiar vista previa anterior
                    const imgContainer = previewContainer.querySelector('.preview-container');
                    if (imgContainer) {
                        imgContainer.innerHTML = '';
                    }
                    
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
                    reader.onload = function(e) {
                        previewImage.src = e.target.result;
                    }
                    reader.readAsDataURL(this.files[0]);
                    
                    // Agregar elementos al DOM
                    imagePreview.appendChild(previewImage);
                    imagePreview.appendChild(tooltip);
                    imagePreview.appendChild(removeBtn);
                    imgContainer.appendChild(imagePreview);
                }
            }
        });
    }
    
    // Vista previa para imágenes adicionales
    const additionalImagesInput = document.getElementById('additionalImages');
    if (additionalImagesInput) {
        additionalImagesInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                // Buscar o mostrar el contenedor de vista previa
                let previewContainer = document.querySelector('.additional-images-preview');
                if (previewContainer) {
                    previewContainer.classList.remove('hidden');
                    
                    // Limpiar vista previa anterior
                    const previewGrid = previewContainer.querySelector('.preview-grid');
                    if (previewGrid) {
                        previewGrid.innerHTML = '';
                        
                        // Crear contador de imágenes
                        const imageCount = document.createElement('p');
                        imageCount.className = 'text-xs text-gray-400 mt-1';
                        imageCount.textContent = `${this.files.length} imagen(es) seleccionada(s)`;
                        previewContainer.querySelector('p').after(imageCount);
                        
                        // Mostrar vista previa de cada imagen
                        Array.from(this.files).forEach((file, index) => {
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
                                
                                // Eliminar la imagen de la lista
                                const dt = new DataTransfer();
                                const files = additionalImagesInput.files;
                                
                                for (let i = 0; i < files.length; i++) {
                                    if (i !== parseInt(imagePreview.dataset.index)) {
                                        dt.items.add(files[i]);
                                    }
                                }
                                
                                additionalImagesInput.files = dt.files;
                                
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
                            });
                            
                            // Leer el archivo y mostrar la vista previa
                            const reader = new FileReader();
                            reader.onload = function(e) {
                                previewImage.src = e.target.result;
                            }
                            reader.readAsDataURL(file);
                            
                            // Agregar elementos al DOM
                            imagePreview.appendChild(previewImage);
                            imagePreview.appendChild(tooltip);
                            imagePreview.appendChild(removeBtn);
                            previewGrid.appendChild(imagePreview);
                        });
                    }
                }
            }
        });
    }
    
    // Animación para botones y efectos visuales
    const enhanceUI = function() {
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
                    setTimeout(() => {
                        ripple.remove();
                    }, 600);
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
    };
    
    // Mejorar la UI con efectos visuales
    enhanceUI();
    
    // Función para resetear las vistas previas cuando se limpia el formulario
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('reset', function() {
            // Ocultar todas las vistas previas
            const previewContainers = document.querySelectorAll('.main-image-preview, .additional-images-preview');
            previewContainers.forEach(container => {
                container.classList.add('hidden');
            });
            
            // Limpiar los contenedores de vista previa
            const previewGrids = document.querySelectorAll('.preview-container, .preview-grid');
            previewGrids.forEach(grid => {
                grid.innerHTML = '';
            });
            
            // Eliminar los contadores de imágenes
            const counters = document.querySelectorAll('.additional-images-preview p + p');
            counters.forEach(counter => counter.remove());
        });
    }
});

function loadProductData(producto) {
    // Cargar datos básicos del producto
    document.getElementById('productId').value = producto.id;
    document.getElementById('productName').value = producto.name;
    document.getElementById('description').value = producto.description;
    document.getElementById('type').value = producto.category;
    document.getElementById('stock').value = producto.stock;
    document.getElementById('price').value = producto.price;
    
    // Si la imagen principal existe, mostrarla en la vista previa
    if (producto.img) {
        const mainImagePreview = document.querySelector('.main-image-preview');
        if (mainImagePreview) {
            mainImagePreview.classList.remove('hidden');
            
            const previewContainer = mainImagePreview.querySelector('.preview-container');
            if (previewContainer) {
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
        }
    }
    
    // Manejador para la eliminación de imágenes existentes
    const setupExistingImagesHandlers = function() {
        // Obtener todos los checkboxes de eliminación de imágenes
        const deleteCheckboxes = document.querySelectorAll('input[name="delete_images"]');
        
        deleteCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // Obtener el contenedor de la imagen
                const imageContainer = this.closest('.existing-image-item');
                
                // Aplicar clase de overlay cuando está marcado
                if (this.checked) {
                    imageContainer.querySelector('img').classList.add('opacity-50');
                    imageContainer.querySelector('.delete-overlay').classList.add('opacity-100');
                } else {
                    imageContainer.querySelector('img').classList.remove('opacity-50');
                    imageContainer.querySelector('.delete-overlay').classList.remove('opacity-100');
                }
            });
        });
    };
    
    // Configurar los manejadores para las imágenes existentes
    setupExistingImagesHandlers();
}

// Además, a continuación agrega este fragmento de código al final de tu DOMContentLoaded event
// Este código garantiza que los manejadores se inicialicen correctamente

document.addEventListener('DOMContentLoaded', function() {
    // Código existente...
    
    // Inicializar los manejadores para las imágenes existentes si estamos en modo edición
    const existingImagesContainer = document.getElementById('existingImagesContainer');
    if (existingImagesContainer) {
        const deleteCheckboxes = document.querySelectorAll('input[name="delete_images"]');
        
        deleteCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // Obtener el contenedor de la imagen
                const imageContainer = this.closest('.existing-image-item');
                
                // Aplicar clase de overlay cuando está marcado
                if (this.checked) {
                    imageContainer.querySelector('img').classList.add('opacity-50');
                    imageContainer.querySelector('.delete-overlay').classList.remove('opacity-0');
                    imageContainer.querySelector('.delete-overlay').classList.add('opacity-100');
                } else {
                    imageContainer.querySelector('img').classList.remove('opacity-50');
                    imageContainer.querySelector('.delete-overlay').classList.add('opacity-0');
                    imageContainer.querySelector('.delete-overlay').classList.remove('opacity-100');
                }
            });
        });
    }
});