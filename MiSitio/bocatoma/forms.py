

from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Resena, Reservacion, Cabana, Actividad, Perfil, Contacto, Pago


class ResenaForm(forms.ModelForm):
    
    calificacion = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        error_messages={
            'required': 'Por favor califica el lugar con estrellas (1 a 5).',
            'min_value': 'La calificación mínima es 1 estrella.',
            'max_value': 'La calificación máxima es 5 estrellas.',
        }
    )
    probabilidad = forms.IntegerField(
        min_value=1,
        max_value=10,
        required=True,
        error_messages={
            'required': 'Por favor indica qué tan probable es que vuelvas (1 a 10).',
            'min_value': 'El valor mínimo es 1.',
            'max_value': 'El valor máximo es 10.',
        }
    )

    class Meta:
        model = Resena
        fields = ['nombre', 'origen', 'calificacion', 'probabilidad', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'id': 'nombre',
                'placeholder': 'Tu nombre completo',
                'required': True,
            }),
            'origen': forms.TextInput(attrs={
                'id': 'origen',
                'placeholder': '¿De dónde nos visitas? (ej. Cd. Victoria, Tampico)',
                'required': True,
            }),
            'mensaje': forms.Textarea(attrs={
                'id': 'mensaje',
                'rows': 5,
                'placeholder': 'Cuéntanos tu experiencia en La Bocatoma...',
                'required': True,
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise ValidationError('Por favor ingresa un nombre válido.')
        return nombre

    def clean_origen(self):
        origen = self.cleaned_data.get('origen', '').strip()
        if len(origen) < 2:
            raise ValidationError('Por favor ingresa tu lugar de procedencia.')
        return origen

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '').strip()
        if len(mensaje) < 5:
            raise ValidationError('El mensaje debe tener al menos 5 caracteres.')
        return mensaje


class RegistroVisitanteForm(UserCreationForm):
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre(s)',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Carlos'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label='Apellidos',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Martínez González'})
    )
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'tu_correo@ejemplo.com'})
    )
    telefono = forms.CharField(
        max_length=20,
        required=True,
        label='Teléfono o WhatsApp',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. 834 123 4567'})
    )
    origen = forms.CharField(
        max_length=120,
        required=False,
        label='Ciudad o Estado de origen',
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Gómez Farías / Monterrey'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            Perfil.objects.update_or_create(
                usuario=user,
                defaults={
                    'telefono': self.cleaned_data.get('telefono', ''),
                    'origen': self.cleaned_data.get('origen', ''),
                }
            )
        return user


class ReservacionForm(forms.ModelForm):
   
    actividades = forms.ModelMultipleChoiceField(
        queryset=Actividad.objects.filter(disponible=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Actividades adicionales que deseas agregar'
    )

    class Meta:
        model = Reservacion
        fields = ['cabana', 'fecha_entrada', 'fecha_salida', 'personas', 'medio_confirmacion', 'actividades']
        widgets = {
            'cabana': forms.Select(attrs={'class': 'form-input-select'}),
            'fecha_entrada': forms.DateInput(attrs={'type': 'date', 'class': 'form-input-date'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date', 'class': 'form-input-date'}),
            'personas': forms.NumberInput(attrs={'min': 1, 'max': 30, 'class': 'form-input-number'}),
            'medio_confirmacion': forms.Select(attrs={'class': 'form-input-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cabana = cleaned_data.get('cabana')
        fecha_entrada = cleaned_data.get('fecha_entrada')
        fecha_salida = cleaned_data.get('fecha_salida')
        personas = cleaned_data.get('personas')

        hoy = timezone.localdate()

        if fecha_entrada and fecha_entrada < hoy:
            self.add_error('fecha_entrada', 'La fecha de entrada no puede ser anterior al día de hoy.')

        if fecha_entrada and fecha_salida:
            if fecha_salida <= fecha_entrada:
                self.add_error('fecha_salida', 'La fecha de salida debe ser posterior a la fecha de entrada.')
            else:
                # Validar que no haya empalme con otra reservación activa (confirmada, recibida o pendiente)
                solapadas = Reservacion.objects.filter(
                    cabana=cabana,
                    estado__in=['confirmada', 'recibida', 'pendiente'],
                    fecha_entrada__lt=fecha_salida,
                    fecha_salida__gt=fecha_entrada
                )
                if self.instance and self.instance.pk:
                    solapadas = solapadas.exclude(pk=self.instance.pk)

                if solapadas.exists():
                    self.add_error(
                        None,
                        f'La cabaña "{cabana.nombre}" ya está reservada en esas fechas. '
                        f'Por favor selecciona otras fechas u otra cabaña disponible.'
                    )

        if cabana and personas:
            if personas > cabana.capacidad:
                self.add_error(
                    'personas',
                    f'La capacidad máxima de la cabaña "{cabana.nombre}" es de {cabana.capacidad} personas.'
                )

        return cleaned_data


def validar_algoritmo_luhn(numero: str) -> bool:
    """Valida que un número de tarjeta cumpla con el algoritmo de Luhn."""
    digitos = [int(d) for d in numero if d.isdigit()]
    if len(digitos) < 13 or len(digitos) > 19:
        return False
    impares = digitos[-1::-2]
    pares = digitos[-2::-2]
    suma = sum(impares)
    for p in pares:
        suma += sum(divmod(p * 2, 10))
    return suma % 10 == 0


class PagoSimuladoForm(forms.Form):
   
    titular = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre en la tarjeta',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. CARLOS MARTINEZ',
            'autocomplete': 'off',
        })
    )
    numero_tarjeta = forms.CharField(
        max_length=23,
        required=True,
        label='Número de tarjeta (16 dígitos)',
        widget=forms.TextInput(attrs={
            'placeholder': '4242 4242 4242 4242',
            'maxlength': '19',
            'autocomplete': 'off',
        })
    )
    mes_vencimiento = forms.ChoiceField(
        choices=[(f"{m:02d}", f"{m:02d}") for m in range(1, 13)],
        required=True,
        label='Mes de vencimiento'
    )
    anio_vencimiento = forms.ChoiceField(
        choices=[(str(y), str(y)) for y in range(2025, 2036)],
        required=True,
        label='Año de vencimiento'
    )
    cvv = forms.CharField(
        max_length=4,
        min_length=3,
        required=True,
        label='CVV (Código de seguridad)',
        widget=forms.PasswordInput(attrs={
            'placeholder': '123',
            'maxlength': '4',
            'autocomplete': 'off',
        })
    )

    def clean_numero_tarjeta(self):
        numero = self.cleaned_data.get('numero_tarjeta', '').replace(' ', '').replace('-', '')
        if not numero.isdigit():
            raise ValidationError('El número de tarjeta solo debe contener dígitos.')
        if len(numero) != 16:
            raise ValidationError('El número de tarjeta debe tener exactamente 16 dígitos.')
        if not validar_algoritmo_luhn(numero):
            raise ValidationError('El número de tarjeta no es válido (falla algoritmo de Luhn). Usa una tarjeta de prueba válida.')
        return numero

    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv', '').strip()
        if not cvv.isdigit():
            raise ValidationError('El CVV debe ser numérico.')
        if len(cvv) not in (3, 4):
            raise ValidationError('El CVV debe tener 3 o 4 dígitos.')
        return cvv

    def clean(self):
        cleaned_data = super().clean()
        mes = cleaned_data.get('mes_vencimiento')
        anio = cleaned_data.get('anio_vencimiento')

        if mes and anio:
            hoy = date.today()
            anio_int = int(anio)
            mes_int = int(mes)
            if anio_int < hoy.year or (anio_int == hoy.year and mes_int < hoy.month):
                self.add_error('mes_vencimiento', 'La tarjeta ingresada ya se encuentra vencida.')

        return cleaned_data


class ContactoForm(forms.ModelForm):
    """
    Formulario ModelForm para la sección de contacto y dudas sobre el parque.
    """
    class Meta:
        model = Contacto
        fields = ['nombre', 'correo', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Tu nombre completo',
                'required': True,
            }),
            'correo': forms.EmailInput(attrs={
                'placeholder': 'tu_correo@ejemplo.com',
                'required': True,
            }),
            'mensaje': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe aquí tu duda, sugerencia o comentario...',
                'required': True,
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise ValidationError('Por favor escribe tu nombre completo.')
        return nombre

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '').strip()
        if len(mensaje) < 10:
            raise ValidationError('El mensaje debe tener al menos 10 caracteres para poder ayudarte mejor.')
        return mensaje
