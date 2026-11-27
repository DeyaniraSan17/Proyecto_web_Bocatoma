from django.urls import path
from . import views

app_name = 'bocatoma'

urlpatterns = [
    # Páginas principales del parque
    path('', views.inicio, name='inicio'),
    path('actividades/', views.actividades, name='actividades'),
    path('cabanas/', views.cabanas, name='cabanas'),
    path('info-bocatoma/', views.info_bocatoma, name='info_bocatoma'),
    path('mi-entorno-limpio/', views.mi_entorno_limpio, name='mi_entorno_limpio'),
    path('naturaleza/', views.naturaleza, name='naturaleza'),
    path('resenas/', views.resenas, name='resenas'),
    path('restaurantes/', views.restaurantes, name='restaurantes'),
    path('contacto/', views.contacto, name='contacto'),

    # Autenticación y cuentas de visitantes
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Flujo de reservaciones y pago simulado
    path('reservar/', views.reservar, name='reservar'),
    path('reservar/<int:cabana_id>/', views.reservar, name='reservar_cabana'),
    path('pagar/<str:folio>/', views.pagar_reservacion, name='pagar_reservacion'),
    path('confirmacion/<str:folio>/', views.confirmacion_reservacion, name='confirmacion_reservacion'),
    path('mis-reservaciones/', views.mis_reservaciones, name='mis_reservaciones'),
    path('cancelar/<str:folio>/', views.cancelar_reservacion, name='cancelar_reservacion'),
]
