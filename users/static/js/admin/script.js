/**
 * NeonTech Admin Panel 
 * Funcionalidades para la gestión de imágenes, precio y sidebar
 */

document.addEventListener('DOMContentLoaded', function() {
    // ==================== Sidebar Toggle ====================
    initSidebar();
    
    // ==================== File Upload & Image Preview ====================
    setupFileDropArea('mainImageDropArea', 'productImage', 'main-image-preview');
    setupFileDropArea('additionalImagesDropArea', 'additionalImages', 'additional-images-preview', true);
    
    // ==================== Initialize Image Previews ====================
    showExistingMainImage();
    initImagePreviews();
    
    // ==================== Existing Images Handlers ====================
    setupExistingImagesHandlers();
});

/**
 * Muestra la imagen principal existente en modo edición
 */
function showExistingMainImage() {
    const currentMainImageInput = document.getElementById('currentMainImage');
    if (!currentMainImageInput) return;
    
    const mainImageUrl = currentMainImageInput.value;
    if (!mainImageUrl) return;
    
    const previewContainer = document.querySelector('.main-image-preview');
    if (!previewContainer) return;
    
    // Mostrar el contenedor de vista previa
    previewContainer.classList.remove('hidden');
    
    // Localizar o crear el contenedor para la imagen
    let imgContainer = previewContainer.querySelector('.preview-container');
    if (!imgContainer) {
        imgContainer = document.createElement('div');
        imgContainer.className = 'preview-container flex justify-center';
        previewContainer.appendChild(imgContainer);
    } else {
        imgContainer.innerHTML = ''; 
    }
    
    // Crear el contenedor para la imagen
    const imagePreview = document.createElement('div');
    imagePreview.className = 'preview-item relative w-64 h-48 overflow-hidden rounded-lg border border-sky-500/30 group';
    
    const previewImage = document.createElement('img');
    previewImage.className = 'w-full h-full object-contain';
    previewImage.src = mainImageUrl;
    
    // Extraer nombre del archivo para el tooltip
    const filenameParts = mainImageUrl.split('/');
    const filename = filenameParts[filenameParts.length - 1];
    
    const tooltip = document.createElement('div');
    tooltip.className = 'image-tooltip';
    tooltip.textContent = filename;
    
    // Botón de eliminación
    const removeBtn = document.createElement('button');
    removeBtn.className = 'preview-actions absolute top-2 right-2 bg-red-500/80 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        previewContainer.classList.add('hidden');
    });
    
    // Ensamblar componentes
    imagePreview.appendChild(previewImage);
    imagePreview.appendChild(tooltip);
    imagePreview.appendChild(removeBtn);
    imgContainer.appendChild(imagePreview);
}

/**
 * Gestiona la funcionalidad del menú lateral (sidebar)
 */
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (!sidebarToggle || !sidebar || !sidebarOverlay) return;
    
    // Alternar visibilidad del sidebar
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    });
    
    // Cerrar sidebar al hacer clic en el overlay
    sidebarOverlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    });
    
    // Ajustar comportamiento en respuesta a cambios de tamaño
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        }
    });
}

/**
 * Configura sistemas de vista previa para imágenes principales y adicionales
 */
function initImagePreviews() {
    // Gestión de la imagen principal
    const mainImageInput = document.getElementById('productImage');
    if (mainImageInput) {
        mainImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                let previewContainer = document.querySelector('.main-image-preview');
                if (!previewContainer) return;
                
                previewContainer.classList.remove('hidden');
                
                // Preparar contenedor 
                const imgContainer = previewContainer.querySelector('.preview-container');
                if (!imgContainer) return;
                imgContainer.innerHTML = '';
                
                // Crear elementos para la vista previa
                const imagePreview = document.createElement('div');
                imagePreview.className = 'preview-item relative w-64 h-48 overflow-hidden rounded-lg border border-sky-500/30 group';
                
                const previewImage = document.createElement('img');
                previewImage.className = 'w-full h-full object-contain';

                const tooltip = document.createElement('div');
                tooltip.className = 'image-tooltip';
                tooltip.textContent = this.files[0].name;
                
                // Configurar botón de eliminación
                const removeBtn = document.createElement('button');
                removeBtn.className = 'preview-actions absolute top-2 right-2 bg-red-500/80 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    mainImageInput.value = '';
                    previewContainer.classList.add('hidden');
                    
                    // Restaurar imagen original si existe
                    const currentMainImageInput = document.getElementById('currentMainImage');
                    if (currentMainImageInput && currentMainImageInput.value) {
                        showExistingMainImage();
                    }
                });
                
                // Cargar y mostrar la imagen
                const reader = new FileReader();
                reader.onload = e => previewImage.src = e.target.result;
                reader.readAsDataURL(this.files[0]);
                
                // Ensamblar componentes
                imagePreview.appendChild(previewImage);
                imagePreview.appendChild(tooltip);
                imagePreview.appendChild(removeBtn);
                imgContainer.appendChild(imagePreview);
            }
        });
    }
    
    // Gestión de imágenes adicionales
    const additionalImagesInput = document.getElementById('additionalImages');
    if (additionalImagesInput) {
        // DataTransfer para gestionar múltiples archivos
        let selectedFiles = new DataTransfer();
        
        additionalImagesInput.addEventListener('change', function(event) {
            if (!this.files || this.files.length === 0) return;
            
            let previewContainer = document.querySelector('.additional-images-preview');
            if (!previewContainer) return;
            
            previewContainer.classList.remove('hidden');
            
            const previewGrid = previewContainer.querySelector('.preview-grid');
            if (!previewGrid) return;
            
            // Combinar archivos existentes con nuevos
            const currentFiles = selectedFiles.files;
            const newFiles = this.files;
            
            const updatedDataTransfer = new DataTransfer();
            
            // Mantener archivos existentes
            for (let i = 0; i < currentFiles.length; i++) {
                updatedDataTransfer.items.add(currentFiles[i]);
            }
            
            // Añadir archivos nuevos
            for (let i = 0; i < newFiles.length; i++) {
                updatedDataTransfer.items.add(newFiles[i]);
            }
            
            // Actualizar colección
            selectedFiles = updatedDataTransfer;
            this.files = selectedFiles.files;
            
            // Regenerar vista previa
            previewGrid.innerHTML = '';
            
            // Crear vista previa para cada archivo
            for (let index = 0; index < selectedFiles.files.length; index++) {
                const file = selectedFiles.files[index];
                
                const imagePreview = document.createElement('div');
                imagePreview.className = 'preview-item relative aspect-square overflow-hidden rounded-lg border border-sky-500/30 group';
                imagePreview.dataset.index = index;
                
                const previewImage = document.createElement('img');
                previewImage.className = 'w-full h-full object-cover';
                
                const tooltip = document.createElement('div');
                tooltip.className = 'image-tooltip';
                tooltip.textContent = file.name;
                
                // Configurar botón de eliminación
                const removeBtn = document.createElement('button');
                removeBtn.className = 'preview-actions absolute top-1 right-1 bg-red-500/80 hover:bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Eliminar archivo del DataTransfer
                    const newSelectedFiles = new DataTransfer();
                    
                    for (let i = 0; i < selectedFiles.files.length; i++) {
                        if (i !== parseInt(imagePreview.dataset.index)) {
                            newSelectedFiles.items.add(selectedFiles.files[i]);
                        }
                    }
                    
                    selectedFiles = newSelectedFiles;
                    additionalImagesInput.files = selectedFiles.files;
                    
                    // Actualizar UI
                    imagePreview.remove();
                    
                    const imageCountElem = previewContainer.querySelector('p + p');
                    if (imageCountElem) {
                        imageCountElem.textContent = `${additionalImagesInput.files.length} imagen(es) seleccionada(s)`;
                    }
                    
                    if (additionalImagesInput.files.length === 0) {
                        previewContainer.classList.add('hidden');
                    }
                    
                    // Reordenar índices
                    const remainingPreviews = previewGrid.querySelectorAll('.preview-item');
                    remainingPreviews.forEach((item, i) => {
                        item.dataset.index = i;
                    });
                });
                
                // Cargar y mostrar la imagen
                const reader = new FileReader();
                reader.onload = e => previewImage.src = e.target.result;
                reader.readAsDataURL(file);
                
                // Ensamblar componentes
                imagePreview.appendChild(previewImage);
                imagePreview.appendChild(tooltip);
                imagePreview.appendChild(removeBtn);
                previewGrid.appendChild(imagePreview);
            }
            
            // Actualizar contador de imágenes
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
 * Configura el área de drag and drop 
 * @param {string} dropAreaId dropAreaId - ID del contenedor para drop
 * @param {string} fileInputId fileInputId - ID del input de tipo file
 * @param {string} previewClass previewClass - Clase del contenedor de vista previa
 * @param {boolean} isMultiple isMultiple - Permite selección múltiple
 */
function setupFileDropArea(dropAreaId, fileInputId, previewClass, isMultiple = false) {
    const dropArea = document.getElementById(dropAreaId);
    const fileInput = document.getElementById(fileInputId);
    
    if (!dropArea || !fileInput) return;
    
    // Configurar atributo multiple
    if (isMultiple) {
        fileInput.setAttribute('multiple', 'multiple');
    } else {
        fileInput.removeAttribute('multiple');
    }
    
    // Prevenir comportamiento por defecto
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    // Efectos visuales durante arrastre
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
            // Modo múltiple
            const dataTransfer = new DataTransfer();
            
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            
            if (files.length === 0) return;
            
            fileInput.files = dataTransfer.files;
        } else if (files.length > 0) {
            // Modo único
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            fileInput.files = dataTransfer.files;
        }
        
        // Activar vista previa
        fileInput.dispatchEvent(new Event('change'));
    });
    
    // Permitir clic para seleccionar
    dropArea.addEventListener('click', () => fileInput.click());
}

/**
 * Gestiona interacciones con imágenes existentes (modo edición)
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
            
            // Aplicar efectos visuales según estado del checkbox
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