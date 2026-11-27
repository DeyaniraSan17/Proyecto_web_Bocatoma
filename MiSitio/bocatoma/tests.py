

from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import Actividad, Cabana, Contacto, Pago, Perfil, Resena, Reservacion
from .forms import (
    ContactoForm,
    PagoSimuladoForm,
    RegistroVisitanteForm,
    ResenaForm,
    ReservacionForm,
    validar_algoritmo_luhn,
)


class BocatomaTestCase(TestCase):
    def setUp(self):
        # Usuario de prueba
        self.user = User.objects.create_user(
            username='turista1',
            password='mypassword123',
            email='turista@ejemplo.com',
            first_name='Laura',
            last_name='Gómez'
        )
        self.perfil = Perfil.objects.create(
            usuario=self.user,
            telefono='834 987 6543',
            origen='Tampico'
        )

        # Cabaña de prueba
        self.cabana = Cabana.objects.create(
            nombre="Cabaña Familiar El Pedregal",
            descripcion="Hermosa cabaña frente al río",
            capacidad=6,
            precio_noche=Decimal('1000.00'),
            disponible=True
        )

        # Actividad de prueba
        self.actividad1 = Actividad.objects.create(
            nombre="Paseo en lancha",
            precio=Decimal('200.00'),
            duracion="1 hora",
            disponible=True
        )
        self.actividad_gratis = Actividad.objects.create(
            nombre="Natación libre",
            precio=Decimal('0.00'),
            duracion="Libre",
            disponible=True
        )

        self.client = Client()

    def test_modelo_actividad_precio_texto(self):
        """Verifica que el precio 0 muestre 'Gratis' y otros muestren el monto."""
        self.assertEqual(self.actividad_gratis.precio_texto, "Gratis")
        self.assertEqual(self.actividad1.precio_texto, "$200.00")

    def test_resena_modelform_y_ligada_a_usuario(self):
        """Punto 1: ModelForm de reseñas valida 1-5, 1-10 y se liga al usuario logueado."""
        self.client.login(username='turista1', password='mypassword123')
        data = {
            'nombre': 'Laura Gómez',
            'origen': 'Tampico',
            'calificacion': 5,
            'probabilidad': 10,
            'mensaje': 'Excelente lugar para descansar y conectar con la naturaleza.',
        }
        form = ResenaForm(data=data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse('bocatoma:resenas'), data)
        self.assertEqual(response.status_code, 302)

        resena = Resena.objects.latest('id')
        self.assertEqual(resena.usuario, self.user)
        self.assertEqual(resena.calificacion, 5)
        self.assertEqual(resena.probabilidad, 10)
        self.assertEqual(resena.estrellas, "★★★★★")

    def test_registro_usuario_form_y_password_amigable(self):
        """Punto 2: Registro con UserCreationForm, contraseña amigable (>= 6 car) y creación de Perfil."""
        data = {
            'username': 'nuevovisitante',
            'first_name': 'Mario',
            'last_name': 'Reyes',
            'email': 'mario@ejemplo.com',
            'telefono': '834 555 7788',
            'origen': 'Victoria',
            'password1': 'facil123',
            'password2': 'facil123',
        }
        form = RegistroVisitanteForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        usuario_creado = form.save()
        self.assertEqual(usuario_creado.email, 'mario@ejemplo.com')
        self.assertTrue(hasattr(usuario_creado, 'perfil'))
        self.assertEqual(usuario_creado.perfil.telefono, '834 555 7788')

    def test_reservacion_validaciones_fechas_y_capacidad(self):
        """Punto 5: Validaciones de fechas posteriores, capacidad y cálculo de total."""
        hoy = date.today()
        entrada = hoy + timedelta(days=2)
        salida_invalida = hoy + timedelta(days=1)
        salida_valida = hoy + timedelta(days=5)

        # Salida antes de entrada debe fallar
        form_invalido = ReservacionForm(data={
            'cabana': self.cabana.id,
            'fecha_entrada': entrada,
            'fecha_salida': salida_invalida,
            'personas': 2,
            'medio_confirmacion': 'correo',
        })
        self.assertFalse(form_invalido.is_valid())
        self.assertIn('fecha_salida', form_invalido.errors)

        # Capacidad excedida debe fallar
        form_capacidad = ReservacionForm(data={
            'cabana': self.cabana.id,
            'fecha_entrada': entrada,
            'fecha_salida': salida_valida,
            'personas': 15,  # Capacidad máxima es 6
            'medio_confirmacion': 'correo',
        })
        self.assertFalse(form_capacidad.is_valid())
        self.assertIn('personas', form_capacidad.errors)

        # Formulario válido
        form_valido = ReservacionForm(data={
            'cabana': self.cabana.id,
            'fecha_entrada': entrada,
            'fecha_salida': salida_valida,
            'personas': 4,
            'medio_confirmacion': 'whatsapp',
            'actividades': [self.actividad1.id],
        })
        self.assertTrue(form_valido.is_valid(), form_valido.errors)

    def test_flujo_completo_reservacion_y_pago_simulado(self):
        """Puntos 5 y 7: Crear reservación, pagar con tarjeta simulada (Luhn) y guardar solo últimos 4 dígitos."""
        self.client.login(username='turista1', password='mypassword123')
        hoy = date.today()
        entrada = hoy + timedelta(days=3)
        salida = hoy + timedelta(days=6)  # 3 noches

        res_data = {
            'cabana': self.cabana.id,
            'fecha_entrada': entrada,
            'fecha_salida': salida,
            'personas': 3,
            'medio_confirmacion': 'whatsapp',
            'actividades': [self.actividad1.id],
        }
        res_post = self.client.post(reverse('bocatoma:reservar'), res_data)
        self.assertEqual(res_post.status_code, 302)

        reserva = Reservacion.objects.get(usuario=self.user)
        self.assertTrue(reserva.folio.startswith('BOC-'))
        self.assertEqual(reserva.estado, 'pendiente')
        # 3 noches * 1000 + 200 de actividad = 3200
        self.assertEqual(reserva.total, Decimal('3200.00'))

        # Pago con tarjeta de prueba (Visa válida por Luhn)
        pago_data = {
            'titular': 'LAURA GOMEZ',
            'numero_tarjeta': '4242424242424242',
            'mes_vencimiento': '12',
            'anio_vencimiento': '2028',
            'cvv': '123',
        }
        pago_form = PagoSimuladoForm(data=pago_data)
        self.assertTrue(pago_form.is_valid(), pago_form.errors)

        pago_post = self.client.post(
            reverse('bocatoma:pagar_reservacion', kwargs={'folio': reserva.folio}),
            pago_data
        )
        self.assertEqual(pago_post.status_code, 302)

        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'confirmada')
        pago = Pago.objects.get(reservacion=reserva)
        self.assertEqual(pago.ultimos4, '4242')
        self.assertNotIn('1111', pago.ultimos4)

    def test_validacion_algoritmo_luhn(self):
        """Punto 7: Algoritmo de Luhn para números de tarjeta."""
        self.assertTrue(validar_algoritmo_luhn('4242424242424242'))
        self.assertTrue(validar_algoritmo_luhn('4532000000000009'))
        self.assertFalse(validar_algoritmo_luhn('4242424242424241'))

    def test_contacto_modelform(self):
        """Punto 11: Formulario de contacto con ModelForm."""
        data = {
            'nombre': 'Roberto Salas',
            'correo': 'roberto@ejemplo.com',
            'mensaje': 'Quisiera saber si permiten mascotas en las cabañas del parque.',
        }
        form = ContactoForm(data=data)
        self.assertTrue(form.is_valid())
        contacto = form.save()
        self.assertEqual(contacto.nombre, 'Roberto Salas')
        self.assertEqual(Contacto.objects.count(), 1)
