from django.db import models
from django.core.validators import MinValueValidator

# Modelos administrados principalmente por el admin
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
    
    def __str__(self):
        return f'Imagen extra de {self.producto.name}'
    
    def get_formatted_price(self):
        """Devuelve el precio formateado con punto decimal"""
        if self.price is None:
            return "0.00"
        return str(self.price).replace(',', '.')

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name='galeria', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/img-per-product')

