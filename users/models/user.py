from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo base de usuario compartido
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
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def is_cliente(self):
        return self.rol == 'cliente'

# Importamos aquí para evitar importaciones circulares
# Nota: Este import debe estar después de la definición de Usuarios
from .admin import Producto

# Modelos compartidos - tanto clientes como administradores interactúan con ellos
class Compra(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Compra #{self.id} de {self.usuario.username}"
    
    # Métodos específicos para administradores
    def actualizar_estado(self, nuevo_estado):
        """Método utilizado por administradores para actualizar el estado de la compra"""
        self.estado = nuevo_estado
        self.save()
        
    # Métodos específicos para clientes
    def get_detalles(self):
        """Devuelve todos los detalles de compra asociados"""
        return self.detalles.all()

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Ahora referencia directamente
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario