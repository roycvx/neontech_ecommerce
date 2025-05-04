from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from ..models.user import Usuarios

class RegisterForm(UserCreationForm):
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