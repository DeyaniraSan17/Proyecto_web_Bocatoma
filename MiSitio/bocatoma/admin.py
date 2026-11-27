
from django import forms
from django.contrib import admin
from django.utils import timezone

from .models import (
    Actividad,
    Cabana,
    Contacto,
    Pago,
    Perfil,
    Resena,
    Reservacion,
)
from .emails import (
    enviar_correo_cabana_lista,
    enviar_correo_cancelacion,
    enviar_correo_confirmacion_pago,
)

# Personalización de títulos del panel administrativo
admin.site.site_header = "Panel de Administración · Parque La Bocatoma"
admin.site.site_title = "La Bocatoma Admin"
admin.site.index_title = "Gestión del Parque Ecoturístico"


@admin.register(Cabana)
class CabanaAdmin(admin.ModelAdmin):
   
    list_display = ('nombre', 'capacidad', 'precio_noche', 'disponible', 'telefono_contacto')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion', 'servicios')
    list_editable = ('disponible', 'precio_noche')


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):

    list_display = ('nombre', 'precio', 'duracion', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'disponible')


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
   
    list_display = (
        'folio',
        'usuario',
        'cabana',
        'fecha_entrada',
        'fecha_salida',
        'personas',
        'total',
        'estado',
        'medio_confirmacion',
        'fecha_recepcion',
    )
    list_filter = ('estado', 'medio_confirmacion', 'fecha_entrada', 'fecha_salida', 'cabana')
    search_fields = (
        'folio',
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__email',
        'cabana__nombre',
    )
    readonly_fields = ('folio', 'fecha_creacion')
    filter_horizontal = ('actividades',)
    actions = ['accion_confirmar', 'accion_marcar_recibida', 'accion_cancelar']

    @admin.action(description="✓ Confirmar reservaciones seleccionadas")
    def accion_confirmar(self, request, queryset):
        actualizadas = 0
        for r in queryset:
            r.estado = 'confirmada'
            r.save()
            enviar_correo_confirmacion_pago(r)
            actualizadas += 1
        self.message_user(
            request,
            f"Se confirmaron {actualizadas} reservación(es) y se enviaron los correos al visitante."
        )

    @admin.action(description="🔑 Marcar como recibidas (Check-in / Cabaña lista)")
    def accion_marcar_recibida(self, request, queryset):
        actualizadas = 0
        ahora = timezone.now()
        for r in queryset:
            r.estado = 'recibida'
            r.fecha_recepcion = ahora
            r.save()
            enviar_correo_cabana_lista(r)
            actualizadas += 1
        self.message_user(
            request,
            f"Se marcaron {actualizadas} reservación(es) como RECIBIDAS (Check-in registrado). "
            f"Se envió el correo 'Tu cabaña está lista' a los visitantes."
        )

    @admin.action(description="✕ Cancelar reservaciones seleccionadas")
    def accion_cancelar(self, request, queryset):
        actualizadas = 0
        for r in queryset:
            r.estado = 'cancelada'
            r.save()
            enviar_correo_cancelacion(r)
            actualizadas += 1
        self.message_user(
            request,
            f"Se cancelaron {actualizadas} reservación(es) y se notificó a los visitantes por correo."
        )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    
    list_display = ('reservacion', 'titular', 'ultimos4', 'monto', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('reservacion__folio', 'titular', 'ultimos4')
    readonly_fields = ('fecha',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Administración de perfiles adicionales de visitantes."""
    list_display = ('usuario', 'telefono', 'origen')
    search_fields = ('usuario__username', 'usuario__email', 'telefono', 'origen')


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    """Mensajes de contacto recibidos desde la web."""
    list_display = ('nombre', 'correo', 'mensaje_corto', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('nombre', 'correo', 'mensaje')
    readonly_fields = ('fecha',)

    @admin.display(description='Mensaje')
    def mensaje_corto(self, obj):
        return obj.mensaje[:70] + ('…' if len(obj.mensaje) > 70 else '')


class ResenaAdminForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = '__all__'
        widgets = {
            'calificacion': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'probabilidad': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """Administración de reseñas del parque."""
    form = ResenaAdminForm
    list_display = (
        'nombre',
        'usuario',
        'origen',
        'calificacion',
        'probabilidad',
        'mensaje_corto',
        'fecha',
    )
    search_fields = ('nombre', 'origen', 'mensaje', 'usuario__username')
    list_filter = ('calificacion', 'fecha')

    @admin.display(description='Mensaje')
    def mensaje_corto(self, obj):
        return obj.mensaje[:60] + ('…' if len(obj.mensaje) > 60 else '')
