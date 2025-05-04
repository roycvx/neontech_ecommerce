from django.db import models
from .user import Usuarios
from .admin import Producto  # Importamos directamente

# Modelos relacionados principalmente con el cliente
class Direccion(models.Model):
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE, related_name='direccion')
    calle = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"

class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Ahora referencia directamente
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.producto.price * self.cantidad
        super().save(*args, **kwargs)
    
class Tarjeta(models.Model):
    nombre = models.CharField(max_length=200)
    serial = models.CharField(max_length=200, unique=True)
    cvv = models.CharField(max_length=4)
    fecha_expiracion = models.DateField()
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.nombre} ({self.serial}) - Monto disponible: {self.saldo}'