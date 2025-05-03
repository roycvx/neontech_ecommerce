from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.conf import settings

# Create your models here.

# Modelo para usuarios
class Usuarios(AbstractUser):
    ROL_CHOICES = (
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='cliente')

    second_name = models.CharField(max_length=50, blank=True, null=True)
    second_lastname = models.CharField(max_length=50, blank=True, null=True)
    verified_account = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

# Modelo para productos
CATEGORIAS = (
    ('laptop', 'Laptop'),
    ('celular', 'Celular'),
)

class Producto(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.ImageField(upload_to='productos/')
    category = models.CharField(max_length=20, choices=CATEGORIAS)
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name='galeria', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/img-per-product')

    def __str__(self):
        return f'Imagen extra de {self.producto.name}'

class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.producto.price * self.cantidad  # Actualiza el subtotal cuando cambie la cantidad
        super().save(*args, **kwargs)

class Compra(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra #{self.id} de {self.usuario.username}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
class Tarjeta(models.Model):
    nombre = models.CharField(max_length=200)
    serial = models.CharField(max_length=200, unique=True)
    cvv = models.CharField(max_length=4)
    fecha_expiracion = models.DateField()  # ahora con validación real
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.nombre} ({self.serial}) - Monto disponible: {self.saldo}'
    
class Direccion(models.Model):
    calle = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"