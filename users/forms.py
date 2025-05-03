from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Usuarios, Direccion

class registerForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        label=_('Primer Nombre'),
        error_messages={'required': _('Este campo es obligatorio.')},
        widget=forms.TextInput(attrs={'placeholder': 'Tu primer nombre'})
    )
    second_name = forms.CharField(
        required=False,
        label=_('Segundo Nombre'),
        widget=forms.TextInput(attrs={'placeholder': 'Tu segundo nombre'})
    )
    last_name = forms.CharField(
        required=True,
        label=_('Primer Apellido'),
        error_messages={'required': _('Este campo es obligatorio.')},
        widget=forms.TextInput(attrs={'placeholder': 'Tu primer apellido'})
    )
    second_lastname = forms.CharField(
        required=False,
        label=_('Segundo Apellido'),
        widget=forms.TextInput(attrs={'placeholder': 'Tu segundo apellido'})
    )
    email = forms.EmailField(
        required=True,
        label=_('Correo Electrónico'),
        error_messages={'required': _('Este campo es obligatorio.'), 'invalid': _('Ingrese un correo válido.')},
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    password1 = forms.CharField(
        label=_('Contraseña'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mínimo 8 caracteres, incluye letras y números'
        }),
        help_text=_('No debe parecerse a tu información personal.')
    )
    password2 = forms.CharField(
        label=_('Confirmar Contraseña'),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'})
    )

    class Meta:
        model = Usuarios
        fields = [
            'first_name',
            'second_name',
            'last_name',
            'second_lastname',
            'email',
            'password1',
            'password2'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuarios.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Ya existe una cuenta asociada a este correo.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        # Asignar username automáticamente si está vacío
        if not user.username:
            base_username = user.email.split('@')[0]
            unique_username = base_username
            count = 1

            while Usuarios.objects.filter(username=unique_username).exists():
                unique_username = f"{base_username}{count}"
                count += 1

            user.username = unique_username

        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={
        'class': 'w-full px-3 py-2 border rounded-lg bg-gray-800 text-white input-glow',
        'placeholder': 'Ingresa tu correo'
    }))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border rounded-lg bg-gray-800 text-white input-glow',
        'placeholder': 'Ingresa tu contraseña'
    }))

#NUEVOO
import datetime
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