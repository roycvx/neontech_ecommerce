from django import forms
from django.utils.translation import gettext_lazy as _
import datetime
from ..models.client import Direccion  # Ajustar según tu modelo

class PaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=16,
        min_length=13,
        label='Número de tarjeta',
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'}),
    )
    card_name = forms.CharField(label='Nombre en la tarjeta')
    expiry_date = forms.CharField(label='Fecha de expiración (MM/AA)')
    cvv = forms.CharField(max_length=4, min_length=3, label='CVV', widget=forms.PasswordInput())

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(" ", "")
        if not number.isdigit():
            raise forms.ValidationError('El número de tarjeta debe contener solo números.')
        if len(number) not in [13, 15, 16]:
            raise forms.ValidationError('Número de tarjeta inválido.')
        return number

    def clean_expiry_date(self):
        expiry = self.cleaned_data['expiry_date']
        try:
            month, year = expiry.split('/')
            month = int(month)
            year = int('20' + year) if len(year) == 2 else int(year)
            now = datetime.datetime.now()
            if month < 1 or month > 12:
                raise forms.ValidationError('Mes inválido.')
            if year < now.year or (year == now.year and month < now.month):
                raise forms.ValidationError('La tarjeta está expirada.')
        except ValueError:
            raise forms.ValidationError('Formato inválido. Usa MM/AA.')
        return expiry