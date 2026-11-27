
import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def enviar_correo_bienvenida(usuario, request=None):
   
    if not usuario.email:
        return False

    asunto = "🌿 ¡Bienvenido al Parque Ecoturístico La Bocatoma!"
    nombre = usuario.first_name or usuario.username
    mensaje = f"""Hola {nombre},

¡Tu cuenta en el Parque Ecoturístico La Bocatoma ha sido creada exitosamente!

Detalles de tu cuenta:
- Usuario: {usuario.username}
- Correo: {usuario.email}

Ya puedes iniciar sesión en nuestro sitio web para:
- Reservar cabañas y hospedajes
- Consultar actividades y precios
- Ver el estado de tus reservaciones
- Dejar tus comentarios y reseñas

¡Esperamos tu pronta visita en Gómez Farías, Tamaulipas!

Atentamente,
Equipo de La Bocatoma
Gómez Farías, Tamaulipas
"""
    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error("Error al enviar correo de bienvenida a %s: %s", usuario.email, e)
        return False


def enviar_correo_confirmacion_pago(reservacion):
    """
    Envía correo de confirmación de pago y reservación con folio, cabaña, fechas y total.
    """
    email = reservacion.usuario.email
    if not email:
        return False

    nombre = reservacion.usuario.first_name or reservacion.usuario.username
    asunto = f"🏕️ Confirmación de Reservación {reservacion.folio} - La Bocatoma"
    
    actividades_list = ", ".join([a.nombre for a in reservacion.actividades.all()])
    if not actividades_list:
        actividades_list = "Ninguna adicional seleccionada"

    mensaje = f"""Estimado(a) {nombre},

¡Tu pago ha sido procesado y tu reservación está CONFIRMADA!

==================================================
RESUMEN DE TU RESERVACIÓN
==================================================
- Folio único: {reservacion.folio}
- Hospedaje: {reservacion.cabana.nombre}
- Check-in (Entrada): {reservacion.fecha_entrada.strftime('%d/%m/%Y')}
- Check-out (Salida): {reservacion.fecha_salida.strftime('%d/%m/%Y')}
- Noches de estancia: {reservacion.noches}
- Personas: {reservacion.personas}
- Actividades agregadas: {actividades_list}
- Total pagado: ${reservacion.total:.2f} MXN
- Medio preferido de avisos: {reservacion.get_medio_confirmacion_display()}
- Estado: CONFIRMADA
==================================================

Recomendaciones para tu llegada:
- Presenta tu folio de reservación ({reservacion.folio}) en la recepción.
- Lleva ropa cómoda y calzado adecuado para actividades acuáticas y senderismo.
- Cuida el entorno natural depositando la basura en su lugar.

¿Dudas o requerimientos especiales? Escríbenos por WhatsApp al 834 274 4432.

¡Te esperamos con los brazos abiertos en Gómez Farías!

Parque Ecoturístico La Bocatoma
"""
    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error("Error al enviar correo de confirmación de reservación %s: %s", reservacion.folio, e)
        return False


def enviar_correo_cabana_lista(reservacion):
    """
    Envía correo notificando que la cabaña está lista y el check-in ha sido completado.
    """
    email = reservacion.usuario.email
    if not email:
        return False

    nombre = reservacion.usuario.first_name or reservacion.usuario.username
    asunto = f"🔑 ¡Tu cabaña está lista! - Folio {reservacion.folio}"
    mensaje = f"""Hola {nombre},

¡Nos complace informarte que tu cabaña '{reservacion.cabana.nombre}' está lista y limpia para ti!

- Folio: {reservacion.folio}
- Check-in registrado: {reservacion.fecha_recepcion.strftime('%d/%m/%Y %H:%M') if reservacion.fecha_recepcion else 'Hoy'}
- Cabaña: {reservacion.cabana.nombre}

Pasa a la recepción del parque para entregarte tus llaves y brindarte indicaciones.

¡Que disfrutes una estancia increíble en La Bocatoma!

Parque Ecoturístico La Bocatoma
"""
    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error("Error al enviar correo de cabaña lista para %s: %s", reservacion.folio, e)
        return False


def enviar_correo_cancelacion(reservacion):
    """
    Envía correo notificando la cancelación de una reservación.
    """
    email = reservacion.usuario.email
    if not email:
        return False

    nombre = reservacion.usuario.first_name or reservacion.usuario.username
    asunto = f"❌ Cancelación de Reservación {reservacion.folio} - La Bocatoma"
    mensaje = f"""Estimado(a) {nombre},

Te informamos que tu reservación con folio {reservacion.folio} para la cabaña '{reservacion.cabana.nombre}' ha sido cancelada.

Detalles:
- Folio: {reservacion.folio}
- Cabaña: {reservacion.cabana.nombre}
- Fechas que habían sido reservadas: del {reservacion.fecha_entrada.strftime('%d/%m/%Y')} al {reservacion.fecha_salida.strftime('%d/%m/%Y')}

Si tienes alguna pregunta o deseas reagendar en otra fecha, estamos a tus órdenes en WhatsApp al 834 274 4432.

Parque Ecoturístico La Bocatoma
"""
    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error("Error al enviar correo de cancelación para %s: %s", reservacion.folio, e)
        return False
