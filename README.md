
# 🚀 NeonTech E-Commerce

[![Python](https://img.shields.io/badge/Python-3.13.2-336ea0?labelColor=000000\&style=for-the-badge\&logo=python\&logoColor=FFFFFF)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?labelColor=000000\&style=for-the-badge\&logo=django\&logoColor=FFFFFF)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/MySQL-9.2.0-bf720d?labelColor=000000\&style=for-the-badge\&logo=mysql\&logoColor=FFFFFF)](https://www.mysql.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-v%204.0-006fb2?labelColor=000000&style=for-the-badge&logo=tailwindcss&logoColor=ffffff&link=https://tailwindcss.com/)](https://tailwindcss.com/)

Una **aplicación web** de comercio electrónico desarrollada en **Django** para venta de laptops y celulares con gestión completa de productos, usuarios y órdenes.

![alt text](/media/img/readme_main.png)

## ✨ Características

### 🛠 Autenticación y Roles

* **Registro de clientes:** formulario de registro para nuevos usuarios.
* **Inicio de sesión:** distingue entre roles de **administrador** y **cliente**.

### ⚙️ Panel de Administración (Admin)

* **CRUD de inventario:**

  * Vista de tabla con todos los productos.
  * Botones de **Crear** (formulario vacío), **Editar** (formulario con datos selecinados) y **Eliminar** (modal de confirmación).
  * **Gestión de imágenes:**

    * **Imagen principal:** utilizada en vistas generales.
    * **Imágenes adicionales:** carpeta `carrusel` dentro de la carpeta del producto.
    * Estructura en `media/productos/{categoria}/{nombre_producto}/` y subcarpeta `carrusel/`.
    * Al actualizar nombre o categoría, se recrea la carpeta y rutas en la base de datos.
  
* **CRUD de usuarios:**

  * Vista de tabla con todos los clientes.
  * Botones de **Crear**, **Editar** (carga datos en formulario) y **Eliminar**.
  * Definición de rol (admin o cliente) en formulario.

* **Gestión de órdenes:**

  * Tabla con todas las órdenes.
  * Actualización de estado de cada orden.

### 🛍️ Interfaz de Cliente

* **Catálogo:** vistas para ver **todos los celulares** o **todas las laptops** en stock.

* **Detalle de producto:** galería de imágenes, descripción, selector de cantidad y botón **Agregar al carrito**.

* **Carrito de compras:**

  * Acceso desde el navbar.
  * Vista de productos seleccionados, cantidades, subtotal y total.
  * Botón **Proceder al pago**.

* **Simulación de pago:**

  * Validación de datos de tarjeta (predefinidas en base de datos con saldo).
  * Verificación de saldo y dirección.
  * Al ser exitoso, muestra alerta de **pago exitoso**, actualiza stock y saldo, y crea nueva orden.

## 🧰 Tecnologías Utilizadas

* **Servidor local:** Laragon (solo gestor de base de datos)
* **Base de datos:** MySQL 9.2.0
* **Lenguaje:** Python 3.13.2
* **Framework web:** Django 5.2
* **Estilos:** Tailwind CSS v4.0

## 📋 Instalación y Configuración Local

**Sigue estos pasos para ejecutar NeonTech en tu máquina local:**

1. **Instalar Python 3.13.2**

2. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/tu-usuario/neontech.git
   cd neontech
   ```

3. **Crear y activar entorno virtual:**

   * Para Windows:

     ```powershell
     python -m venv .venv
      .venv\Scripts\Activate.ps1
     ```

   * Para Git Bash (Windows):

     ```bash
     python -m venv .venv
     source .venv/Scripts/activate
     ```

4. **Configurar base de datos en phpMyAdmin:**

   * Crea un usuario con permisos y define su contraseña.
   * Importa el archivo `db_dump.sql` desde la raíz del proyecto.

5. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

6. **Archivo de entorno:**

   * Copia `.env.example` a `.env` y ajusta los valores según tu configuración local:

     ```ini
     DEBUG=False
     SECRET_KEY=tu_secret_key
     DATABASE_URL=mysql://usuario:contraseña@127.0.0.1:3306/nombre_base_de_datos
     ```

7. **Ejecutar servidor de desarrollo:**

   ```bash
   python manage.py runserver
   ```

   Haz Ctrl + clic en `http://127.0.0.1:8000/` para abrirlo en tu navegador.

8. **Credenciales Admin:**

   * **Correo Electrónico:** `profesor@utp.aca.pa`
   * **Contraseña:** ProfesorArauz

9. **Registro de Usuario Cliente:**

   * **Registro de Cliente (La Contraseña debe tener):**
   * Debe tener mayúscula.
   * Debe tener mínimo 8 caracteres.
   * No debe parecerse al nombre, apellido o correo del usuario.

## 📂 Estructura del Proyecto

```bash
NeonTech/
│
├── media/                   # Archivos multimedia subidos
│   └── productos/           # Imágenes de productos organizadas por categoría
│       ├── celulares/       # Imágenes de celulares
│       └── laptops/         # Imágenes de laptops
│
├── neontech/                # Directorio principal del proyecto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Configuración del proyecto
│   ├── urls.py              # URLs principales
│   └── wsgi.py
│
├── users/                          # Aplicación del Comercio 
│   ├── templates/                  # Plantillas HTML
│   │   └── users/                  
│   │       ├── admin_dashboard/    # Templates de administrador
│   │       │   └── partials/       # Fragmentos reutilizables
│   │       ├── client_dashboard/   # Templates de cliente
│   │       │   └── partials/       # Fragmentos reutilizables
│   │       ├── auth/               # Templates de Inicio de sesión y registro 
│   │       ├──partials/            # Fragmentos reutilizables
│   │       └──start_page.html      # Pagina Principal o de Inicio 
│   │
│   ├── static/                     # Archivos estáticos específicos
│   │   ├── css/                    # Estilos CSS
│   │   │   ├── admin/              # Estilos para el lado de administrador
│   │   │   ├── client/             # Estilos para el lado de cliente
│   │   │   ├── auth/               # Estilos para la página Inicio de sesión y registro 
│   │   │   └── start_page.css      # Estilos Principal o de Inicio 
│   │   │
│   │   ├── js/                  # Scripts JavaScript
│   │   │   ├── admin/           # Scripts para el lado de administrador
│   │   │   └── client/          # Scripts para el lado de cliente
│   │   │
│   │   └── img/                 # Imágenes estáticas
│   │
│   ├── forms/                   # Formularios
│   │   ├── __init__.py
│   │   ├── admin_forms.py       # Formularios específicos para administrador
│   │   ├── client_forms.py      # Formularios específicos para cliente
│   │   └── auth_forms.py        # Formularios compartidos (login, registro)
│   │
│   ├── migrations/              # Migraciones de base de datos
│   │   └── __init__.py
│   │
│   ├── models/                  # Modelos de datos
│   │   ├── __init__.py
│   │   ├── user.py              # Modelo base de usuario
│   │   ├── admin.py             # Modelos específicos para administrador
│   │   └── client.py            # Modelos específicos para cliente
│   │
│   ├── templatetags/            # Tags personalizados para plantillas
│   │
│   ├── views/                   # Vistas y lógica de negocio
│   │   ├── __init__.py
│   │   ├── admin_views.py       # Vistas del panel de administrador
│   │   ├── client_views.py      # Vistas del panel de cliente
│   │   └── auth_views.py        # Vistas compartidas (login, registro)
│   │
│   ├── urls.py                  # Rutas específicas de la app 
│   └── __init__.py
│
├── .env                         # Variables de entorno
├── .venv                        # Entorno Virtual
├── .gitignore                   # Archivos ignorados por Git
├── manage.py                    # Script de administración de Django
├── README.md                    # Documentación del proyecto
└── requirements.txt             # Dependencias Python
```

## 📷 Capturas de Pantalla

### 🛠️ Interfaz del administrador

*A continuación se muestran algunas vistas de la interfaz destinada al panel de administración.*

![alt text](/media/img/admin_readme.png)

### 🛒 Interfaz del cliente

*Estas son algunas vistas de la interfaz que verá el cliente final al navegar por el sitio.*

![alt text](/media/img/client_readme.png)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Para contribuir:

1. Haz un fork del proyecto.
2. Crea una rama (`git switch -c feature/nombre`).
3. Realiza tus cambios y haz commit siguiendo [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/) (ej: `git commit -m "feat: agrega nuevo componente"`).
4. Envía tus cambios (`git push origin feature/nombre`).
5. Abre un pull request.
