from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Perfil(models.Model):
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono / WhatsApp'
    )
    origen = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Ciudad o lugar de procedencia'
    )

    class Meta:
        verbose_name = 'Perfil de Visitante'
        verbose_name_plural = 'Perfiles de Visitantes'

    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name() or self.usuario.username}"


class Resena(models.Model):
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resenas',
        verbose_name='Usuario que reseña'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    origen = models.CharField(max_length=100, verbose_name='Lugar de origen')
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Calificación (1 a 5 estrellas)'
    )
    probabilidad = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Probabilidad de volver (1 a 10)'
    )
    mensaje = models.TextField(verbose_name='Experiencia / Opinión')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')

    @property
    def estrellas(self):
        """Devuelve representación visual de estrellas amarillas/vacías."""
        return "★" * self.calificacion + "☆" * (5 - self.calificacion)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'

    def __str__(self):
        return f"{self.nombre} ({self.calificacion}★)"


class Actividad(models.Model):
    """
    Actividades ecoturísticas disponibles en el parque con precios administrables.
    """
    nombre = models.CharField(max_length=150, verbose_name='Nombre de la actividad')
    descripcion = models.TextField(blank=True, verbose_name='Descripción de la actividad')
    precio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name='Precio ($ MXN)'
    )
    duracion = models.CharField(
        max_length=80,
        blank=True,
        verbose_name='Duración estimada (ej. 40 min, 1 hora)'
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name='¿Actividad disponible?'
    )
    foto = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Ruta de imagen o estático (ej. bocatoma/img/lancha33.jpg)'
    )

    @property
    def precio_texto(self):
       
        if self.precio == 0:
            return "Gratis"
        return f"${self.precio:.2f}"

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f"{self.nombre} - {self.precio_texto}"


class Cabana(models.Model):
    
    nombre = models.CharField(max_length=150, verbose_name='Nombre del hospedaje')
    descripcion = models.TextField(verbose_name='Descripción de las instalaciones')
    capacidad = models.PositiveIntegerField(
        default=4,
        verbose_name='Capacidad máxima (personas)'
    )
    precio_noche = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio por noche ($ MXN)'
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name='¿Disponible para reservar?'
    )
    foto = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Foto principal (ruta estática o enlace)'
    )
    servicios = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Servicios incluidos (Alberca, Asador, WiFi, etc.)'
    )
    telefono_contacto = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono de contacto'
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cabaña / Hospedaje'
        verbose_name_plural = 'Cabañas y Hospedajes'

    def __str__(self):
        return f"{self.nombre} (Capacidad: {self.capacidad} personas - ${self.precio_noche}/noche)"


class Reservacion(models.Model):
   
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('recibida', 'Recibida (Check-in hecho)'),
    ]

    MEDIO_CHOICES = [
        ('correo', 'Correo Electrónico'),
        ('whatsapp', 'WhatsApp'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservaciones',
        verbose_name='Visitante que reserva'
    )
    cabana = models.ForeignKey(
        Cabana,
        on_delete=models.CASCADE,
        related_name='reservaciones',
        verbose_name='Cabaña elegida'
    )
    fecha_entrada = models.DateField(verbose_name='Fecha de entrada (Check-in)')
    fecha_salida = models.DateField(verbose_name='Fecha de salida (Check-out)')
    personas = models.PositiveIntegerField(default=1, verbose_name='Número de personas')
    folio = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Folio único'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado de la reservación'
    )
    medio_confirmacion = models.CharField(
        max_length=20,
        choices=MEDIO_CHOICES,
        default='correo',
        verbose_name='Medio de confirmación preferido'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Total a pagar ($ MXN)'
    )
    actividades = models.ManyToManyField(
        Actividad,
        blank=True,
        related_name='reservaciones',
        verbose_name='Actividades agregadas'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    fecha_recepcion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha y hora de recepción (Check-in)'
    )

    @property
    def noches(self):
        """Calcula el número de noches de la estancia."""
        if self.fecha_salida and self.fecha_entrada:
            delta = (self.fecha_salida - self.fecha_entrada).days
            return max(delta, 1)
        return 1

    def generar_folio(self):
        """Genera un folio consecutivo y legible tipo BOC-0001."""
        ultimo = Reservacion.objects.order_by('-id').first()
        siguiente_id = 1 if not ultimo else ultimo.id + 1
        return f"BOC-{siguiente_id:04d}"

    def save(self, *args, **kwargs):
        if not self.folio:
            self.folio = self.generar_folio()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'

    def __str__(self):
        return f"Reservación {self.folio} - {self.cabana.nombre} ({self.usuario.username}) [{self.get_estado_display()}]"


class Pago(models.Model):
    """
    Registro del pago simulado con tarjeta de la reservación.
    Por seguridad NUNCA se almacena el número de tarjeta completo ni el CVV,
    solamente los últimos 4 dígitos.
    """
    reservacion = models.OneToOneField(
        Reservacion,
        on_delete=models.CASCADE,
        related_name='pago',
        verbose_name='Reservación asociada'
    )
    titular = models.CharField(max_length=150, verbose_name='Nombre del titular')
    ultimos4 = models.CharField(max_length=4, verbose_name='Últimos 4 dígitos')
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto pagado ($ MXN)'
    )
    estado = models.CharField(
        max_length=20,
        default='aprobado',
        verbose_name='Estado del pago'
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora del pago')

    class Meta:
        verbose_name = 'Pago con Tarjeta'
        verbose_name_plural = 'Pagos con Tarjeta'

    def __str__(self):
        return f"Pago {self.reservacion.folio} - ${self.monto} (Terminación: ****{self.ultimos4})"


class Contacto(models.Model):
    """
    Mensajes y dudas enviadas por visitantes mediante el formulario de contacto.
    """
    nombre = models.CharField(max_length=100, verbose_name='Nombre completo')
    correo = models.EmailField(verbose_name='Correo electrónico')
    mensaje = models.TextField(verbose_name='Mensaje o duda')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Mensaje de Contacto'
        verbose_name_plural = 'Mensajes de Contacto'

    def __str__(self):
        return f"Contacto de {self.nombre} ({self.correo})"
