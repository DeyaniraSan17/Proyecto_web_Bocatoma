

import re
import urllib.parse
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import Actividad, Cabana, Contacto, Pago, Resena, Reservacion
from .forms import (
    ContactoForm,
    PagoSimuladoForm,
    RegistroVisitanteForm,
    ResenaForm,
    ReservacionForm,
)
from .emails import (
    enviar_correo_bienvenida,
    enviar_correo_cancelacion,
    enviar_correo_confirmacion_pago,
)

NUMERO_WHATSAPP_PARQUE = "5218342744432"


def inicio(request):
    """Página principal de bienvenida del parque."""
    return render(request, 'bocatoma/inicio.html')


def actividades(request):
    """
    Muestra la lista de actividades ecoturísticas desde la base de datos con precios administrables.
    Si el precio es 0, la plantilla muestra 'Gratis'.
    """
    lista = Actividad.objects.filter(disponible=True)
    return render(request, 'bocatoma/actividades.html', {'actividades': lista})


def cabanas(request):
    """
    Muestra las cabañas y opciones de hospedaje disponibles desde la base de datos.
    Permite ver precios, servicios y reservar directamente.
    """
    lista = Cabana.objects.filter(disponible=True)
    return render(request, 'bocatoma/cabanas.html', {'cabanas': lista})


@login_required
def reservar(request, cabana_id=None):
    """
    Formulario para que un visitante registrado reserve una cabaña.
    Calcula el total por noches y permite agregar actividades opcionales.
    """
    cabana_seleccionada = None
    if cabana_id:
        cabana_seleccionada = get_object_or_404(Cabana, id=cabana_id, disponible=True)
    elif request.GET.get('cabana'):
        cabana_seleccionada = Cabana.objects.filter(id=request.GET.get('cabana'), disponible=True).first()

    if request.method == 'POST':
        form = ReservacionForm(request.POST)
        if form.is_valid():
            reservacion = form.save(commit=False)
            reservacion.usuario = request.user

            # Calcular total base: noches x precio de cabaña
            noches = reservacion.noches
            total = Decimal(str(reservacion.cabana.precio_noche)) * Decimal(str(noches))
            reservacion.total = total
            reservacion.save()

            # Guardar actividades ManyToMany
            form.save_m2m()

            # Sumar actividades seleccionadas al total
            total_actividades = sum(Decimal(str(a.precio)) for a in reservacion.actividades.all())
            reservacion.total += total_actividades
            reservacion.save()

            messages.success(
                request,
                f"¡Reservación creada con éxito! Folio: {reservacion.folio}. "
                f"Por favor completa el pago simulado para confirmarla."
            )
            return redirect('bocatoma:pagar_reservacion', folio=reservacion.folio)
        else:
            messages.error(request, "Por favor corrige los errores señalados en el formulario de reservación.")
    else:
        initial_data = {}
        if cabana_seleccionada:
            initial_data['cabana'] = cabana_seleccionada
        form = ReservacionForm(initial=initial_data)

    return render(request, 'bocatoma/reservar.html', {
        'form': form,
        'cabana_seleccionada': cabana_seleccionada,
    })


@login_required
def pagar_reservacion(request, folio):
    """
    Procesa el pago con tarjeta SIMULADO.
    Valida formato de tarjeta con Luhn, fecha de expiración y CVV.
    NUNCA guarda el número completo ni CVV, solo los últimos 4 dígitos.
    Al pagar con éxito la reservación cambia a 'confirmada'.
    """
    reservacion = get_object_or_404(Reservacion, folio=folio, usuario=request.user)

    # Si ya fue pagada o no está pendiente, redirigir a confirmación
    if reservacion.estado in ['confirmada', 'recibida']:
        messages.info(request, f"La reservación {reservacion.folio} ya se encuentra confirmada.")
        return redirect('bocatoma:confirmacion_reservacion', folio=reservacion.folio)

    if request.method == 'POST':
        form = PagoSimuladoForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero_tarjeta']
            ultimos4 = numero[-4:]
            titular = form.cleaned_data['titular']

            # Registrar pago en base de datos
            pago = Pago.objects.create(
                reservacion=reservacion,
                titular=titular,
                ultimos4=ultimos4,
                monto=reservacion.total,
                estado='aprobado',
            )

            # Cambiar estado de reservación a confirmada
            reservacion.estado = 'confirmada'
            reservacion.save()

            # Enviar correo de confirmación de pago
            enviar_correo_confirmacion_pago(reservacion)

            messages.success(
                request,
                f"¡Pago simulado de ${reservacion.total:.2f} MXN aprobado con éxito! "
                f"Tu reservación con folio {reservacion.folio} ha sido confirmada."
            )
            return redirect('bocatoma:confirmacion_reservacion', folio=reservacion.folio)
        else:
            messages.error(request, "Error en los datos de la tarjeta. Revisa los datos de prueba.")
    else:
        form = PagoSimuladoForm(initial={
            'titular': (request.user.get_full_name() or request.user.username).upper(),
        })

    return render(request, 'bocatoma/pago.html', {
        'form': form,
        'reservacion': reservacion,
    })


def limpiar_telefono_whatsapp(tel):
    """Limpia y formatea un número telefónico para WhatsApp (con código de país México 52/521)."""
    if not tel:
        return ""
    digits = re.sub(r'\D', '', str(tel))
    if len(digits) == 10:
        return f"521{digits}"
    elif len(digits) == 12 and digits.startswith("52"):
        return f"521{digits[2:]}"
    elif len(digits) == 13 and digits.startswith("521"):
        return digits
    return digits


@login_required
def confirmacion_reservacion(request, folio):
    """
    Página de confirmación con folio, resumen de reservación y enlaces de WhatsApp
    tanto para el propio visitante como para el parque.
    """
    reservacion = get_object_or_404(Reservacion, folio=folio, usuario=request.user)

    perfil = getattr(reservacion.usuario, 'perfil', None)
    telefono_usuario = perfil.telefono if perfil else ""
    telefono_wa = limpiar_telefono_whatsapp(telefono_usuario)

    actividades_str = ", ".join([a.nombre for a in reservacion.actividades.all()])
    if not actividades_str:
        actividades_str = "Ninguna"

    # Mensaje completo de comprobante para WhatsApp
    noches_txt = f"{reservacion.noches} noche{'s' if reservacion.noches > 1 else ''}"
    texto_comprobante = (
        f"🌿 *COMPROBANTE DE RESERVACIÓN - LA BOCATOMA* 🌿\n\n"
        f"¡Hola {reservacion.usuario.get_full_name() or reservacion.usuario.username}!\n"
        f"Tu reservación está *CONFIRMADA*.\n\n"
        f"📋 *Folio:* {reservacion.folio}\n"
        f"🏡 *Hospedaje:* {reservacion.cabana.nombre}\n"
        f"📅 *Entrada:* {reservacion.fecha_entrada.strftime('%d/%m/%Y')}\n"
        f"📅 *Salida:* {reservacion.fecha_salida.strftime('%d/%m/%Y')} ({noches_txt})\n"
        f"👥 *Personas:* {reservacion.personas}\n"
        f"🚣 *Actividades:* {actividades_str}\n"
        f"💳 *Total Pagado:* ${reservacion.total:.2f} MXN\n"
        f"📌 *Estado:* Confirmada ✅\n\n"
        f"¡Te esperamos en Gómez Farías, Tamaulipas! 🏞️"
    )
    texto_encoded = urllib.parse.quote(texto_comprobante)

    # 1. Enlace para el WhatsApp del propio visitante (si tiene número registrado)
    url_whatsapp_usuario = f"https://wa.me/{telefono_wa}?text={texto_encoded}" if telefono_wa else None

    # 2. Enlace general para compartir a cualquier chat de WhatsApp (o a sí mismo)
    url_whatsapp_compartir = f"https://api.whatsapp.com/send?text={texto_encoded}"

    # 3. Enlace para notificar o consultar al WhatsApp oficial del parque
    url_whatsapp_parque = f"https://wa.me/{NUMERO_WHATSAPP_PARQUE}?text={texto_encoded}"

    return render(request, 'bocatoma/confirmacion.html', {
        'reservacion': reservacion,
        'telefono_usuario': telefono_usuario,
        'url_whatsapp': url_whatsapp_usuario or url_whatsapp_compartir,
        'url_whatsapp_usuario': url_whatsapp_usuario,
        'url_whatsapp_compartir': url_whatsapp_compartir,
        'url_whatsapp_parque': url_whatsapp_parque,
    })


@login_required
def mis_reservaciones(request):
    """
    Panel de visitante para consultar el historial de reservaciones, su estado,
    posibilidad de cancelar las pendientes y enlace a WhatsApp.
    """
    lista = request.user.reservaciones.all().order_by('-fecha_creacion')
    total_reservas = lista.count()
    confirmadas = lista.filter(estado='confirmada').count()
    pendientes = lista.filter(estado='pendiente').count()
    recibidas = lista.filter(estado='recibida').count()

    # Añadir URL de WhatsApp para cada reservación
    for r in lista:
        texto = (
            f"Reservación {r.folio} ({r.get_estado_display()}), "
            f"cabaña {r.cabana.nombre}, del {r.fecha_entrada.strftime('%d/%m/%Y')} al {r.fecha_salida.strftime('%d/%m/%Y')}."
        )
        r.url_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP_PARQUE}?text={urllib.parse.quote(texto)}"

    return render(request, 'bocatoma/mis_reservaciones.html', {
        'reservaciones': lista,
        'total_reservas': total_reservas,
        'confirmadas': confirmadas,
        'pendientes': pendientes,
        'recibidas': recibidas,
    })


@login_required
def cancelar_reservacion(request, folio):
    """
    Permite al visitante cancelar una reservación que esté en estado 'pendiente'.
    """
    reservacion = get_object_or_404(Reservacion, folio=folio, usuario=request.user)

    if request.method == 'POST':
        if reservacion.estado == 'recibida':
            messages.error(request, "No se puede cancelar una estancia que ya fue recibida (check-in realizado).")
        else:
            reservacion.estado = 'cancelada'
            reservacion.save()
            enviar_correo_cancelacion(reservacion)
            messages.success(request, f"La reservación {reservacion.folio} ha sido cancelada correctamente.")
        return redirect('bocatoma:mis_reservaciones')

    return render(request, 'bocatoma/cancelar_reservacion.html', {
        'reservacion': reservacion,
    })


def resenas(request):
    """
    Página de reseñas procesada con ModelForm (forms.py).
    Requiere inicio de sesión para publicar una reseña (igual que en reservaciones).
    Los visitantes no autenticados pueden ver las reseñas existentes y son guiados al login para publicar.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, "Por favor inicia sesión con tu cuenta para dejar una reseña.")
            return redirect(f"{reverse('bocatoma:login')}?next={reverse('bocatoma:resenas')}")

        form = ResenaForm(request.POST)
        if form.is_valid():
            nueva_resena = form.save(commit=False)
            nueva_resena.usuario = request.user
            nueva_resena.save()
            messages.success(request, "🌿 ¡Muchas gracias! Tu reseña ha sido guardada exitosamente.")
            return redirect('bocatoma:resenas')
        else:
            messages.error(request, "Por favor revisa los campos de tu reseña.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['nombre'] = request.user.get_full_name() or request.user.username
            if hasattr(request.user, 'perfil') and request.user.perfil.origen:
                initial_data['origen'] = request.user.perfil.origen
        form = ResenaForm(initial=initial_data)

    lista = Resena.objects.all().order_by('-fecha')
    promedio = lista.aggregate(p=Avg('calificacion'))['p'] or 0

    return render(request, 'bocatoma/resenas.html', {
        'form': form,
        'resenas': lista,
        'total': lista.count(),
        'promedio': promedio,
    })


def contacto(request):
    """
    Página y formulario de contacto con ModelForm.
    Guarda mensajes en SQLite y muestra feedback con django.contrib.messages.
    """
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "🌿 ¡Mensaje enviado con éxito! En el Parque La Bocatoma nos pondremos en contacto contigo a la brevedad."
            )
            return redirect('bocatoma:contacto')
        else:
            messages.error(request, "Por favor corrige los datos del formulario de contacto.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['nombre'] = request.user.get_full_name() or request.user.username
            initial_data['correo'] = request.user.email
        form = ContactoForm(initial=initial_data)

    return render(request, 'bocatoma/contacto.html', {'form': form})


def registro_usuario(request):
    """
    Registro de nuevos visitantes con UserCreationForm personalizado.
    Valida contraseñas de forma amigable (mínimo 6 caracteres, no similar al usuario)
    y envía correo de bienvenida confirmando el registro.
    """
    if request.user.is_authenticated:
        return redirect('bocatoma:inicio')

    if request.method == 'POST':
        form = RegistroVisitanteForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            enviar_correo_bienvenida(usuario, request)
            messages.success(
                request,
                f"🌿 ¡Bienvenido(a), {usuario.first_name or usuario.username}! Tu cuenta ha sido creada exitosamente. "
                f"Te hemos enviado un correo de confirmación. Ya puedes iniciar sesión con tu usuario y contraseña."
            )
            return redirect('bocatoma:login')
        else:
            messages.error(request, "Por favor revisa los datos de registro señalados a continuación.")
    else:
        form = RegistroVisitanteForm()

    return render(request, 'bocatoma/registro.html', {'form': form})


def login_usuario(request):
    """
    Inicio de sesión con AuthenticationForm nativo de Django.
    """
    if request.user.is_authenticated:
        return redirect('bocatoma:mis_reservaciones')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Hola de nuevo, {user.first_name or user.username}! Has iniciado sesión.")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('bocatoma:mis_reservaciones')
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Por favor inténtalo de nuevo.")
    else:
        form = AuthenticationForm()

    return render(request, 'bocatoma/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


def logout_usuario(request):
    """
    Cierre de sesión seguro con Django.
    """
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente. ¡Esperamos verte pronto!")
    return redirect('bocatoma:inicio')


def info_bocatoma(request):
    """Página informativa Sobre Nosotros."""
    return render(request, 'bocatoma/info_bocatoma.html')


def mi_entorno_limpio(request):
    """Página sobre cuidado ambiental y entorno limpio."""
    return render(request, 'bocatoma/mi_entorno_limpio.html')


def naturaleza(request):
    """Página sobre flora y fauna del parque."""
    return render(request, 'bocatoma/naturaleza.html')


def restaurantes(request):
    """Página sobre restaurantes y gastronomía."""
    return render(request, 'bocatoma/restaurantes.html')
