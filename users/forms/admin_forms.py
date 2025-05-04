from django import forms
from django.utils.translation import gettext_lazy as _

# Asumiendo que tienes un modelo de Producto
class ProductForm(forms.ModelForm):
    """
    Formulario para CRUD de productos
    """
    name = forms.CharField(
        label=_('Nombre del producto'),
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto'})
    )
    
    description = forms.CharField(
        label=_('Descripción'),
        widget=forms.Textarea(attrs={'placeholder': 'Descripción del producto', 'rows': 3})
    )
    
    price = forms.DecimalField(
        label=_('Precio'),
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )
    
    stock = forms.IntegerField(
        label=_('Cantidad en stock'),
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': '0'})
    )
    
    category = forms.ChoiceField(
        label=_('Categoría'),
        choices=[
            ('laptops', _('Laptops')),
            ('phones', _('Teléfonos')),
            ('accessories', _('Accesorios'))
        ]
    )
    
    is_active = forms.BooleanField(
        label=_('Producto activo'),
        required=False,
        initial=True
    )
    
    # Añadir más campos según necesidades
    
    class Meta:
        # Ajustar según tu modelo real
        model = None  # Cambia a tu modelo de Producto 
        fields = ['name', 'description', 'price', 'stock', 'category', 'is_active']


class OrderStatusForm(forms.Form):
    """
    Formulario para actualizar el estado de las órdenes/compras
    """
    status = forms.ChoiceField(
        label=_('Estado de la orden'),
        choices=[
            ('pending', _('Pendiente')),
            ('processing', _('Procesando')),
            ('shipped', _('Enviado')),
            ('delivered', _('Entregado')),
            ('cancelled', _('Cancelado'))
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    tracking_number = forms.CharField(
        label=_('Número de seguimiento'),
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Número de seguimiento (opcional)'})
    )
    
    notes = forms.CharField(
        label=_('Notas'),
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Notas administrativas', 'rows': 2})
    )