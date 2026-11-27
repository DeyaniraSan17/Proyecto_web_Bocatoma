import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiSitio.settings')
django.setup()

from django.contrib.auth.models import User
from bocatoma.models import Cabana, Actividad, Perfil, Contacto

print("--- Poblando datos iniciales para La Bocatoma ---")

# 1. Cabañas
cabanas_data = [
    {
        'id': 1,
        'nombre': "Cabañas El Pedregal",
        'descripcion': "Cabañas familiares y dobles con alberca, asador, Sky, Netflix y WiFi en un entorno natural único junto al río.",
        'capacidad': 6,
        'precio_noche': 1200.00,
        'disponible': True,
        'foto': "bocatoma/img/Cabana_el_pedregall.jpg",
        'servicios': "Alberca, Mesas, Asador, Sky, Netflix, WiFi",
        'telefono_contacto': "812 018 4777",
    },
    {
        'id': 2,
        'nombre': "Hotel 'El Barco'",
        'descripcion': "Habitaciones cómodas con clima, alberca, mesas, asador, palapa y WiFi para disfrutar de La Bocatoma.",
        'capacidad': 8,
        'precio_noche': 950.00,
        'disponible': True,
        'foto': "bocatoma/img/Hotel_barco.jpg",
        'servicios': "Alberca, Mesa, Asador, Palapa, WiFi, Clima",
        'telefono_contacto': "831 114 4562",
    },
]

for c in cabanas_data:
    obj, created = Cabana.objects.update_or_create(
        id=c['id'],
        defaults=c
    )
    print(f"Cabaña: {obj.nombre} ({'creada' if created else 'actualizada'})")

# 2. Actividades
actividades_data = [
    {
        'nombre': "Paseo en lancha",
        'descripcion': "Paseo en lancha por el río con capacidad para 5 personas.",
        'precio': 200.00,
        'duracion': "5 personas",
        'disponible': True,
        'foto': "bocatoma/img/lancha33.jpg",
    },
    {
        'nombre': "Tirolesa",
        'descripcion': "Atracción extrema sobrevolando el río de La Bocatoma con equipo de seguridad.",
        'precio': 150.00,
        'duracion': "Por persona",
        'disponible': True,
        'foto': "bocatoma/img/tirolesaa.jpg",
    },
    {
        'nombre': "Puente Colgante",
        'descripcion': "Cruce y vista panorámica por el icónico puente colgante.",
        'precio': 15.00,
        'duracion': "Paseo",
        'disponible': True,
        'foto': "bocatoma/img/puente_boca.jpg",
    },
    {
        'nombre': "Paseo en Kayak",
        'descripcion': "Renta de kayak para remar por las aguas tranquilas del río.",
        'precio': 150.00,
        'duracion': "1 hora",
        'disponible': True,
        'foto': "bocatoma/img/kayakkk.jpg",
    },
    {
        'nombre': "Paseo en Bicicleta",
        'descripcion': "Renta de bicicleta de montaña para recorrer los senderos ecoturísticos.",
        'precio': 100.00,
        'duracion': "1 hora",
        'disponible': True,
        'foto': "bocatoma/img/bicicletas.jpg",
    },
    {
        'nombre': "Acampar",
        'descripcion': "Espacio de camping seguro con derecho a sanitarios e iluminación.",
        'precio': 150.00,
        'duracion': "Por noche",
        'disponible': True,
        'foto': "bocatoma/img/ACAMPAR1.jpg",
    },
    {
        'nombre': "Senderismo a la Poza Azul",
        'descripcion': "Recorrido guiado de 500 metros hacia el manantial de aguas turquesas de la Poza Azul.",
        'precio': 150.00,
        'duracion': "Guiado",
        'disponible': True,
        'foto': "bocatoma/img/senderismo.jpg",
    },
    {
        'nombre': "Paseo en Cuatrimoto",
        'descripcion': "Recorrido guiado en cuatrimoto por brechas y terracería.",
        'precio': 300.00,
        'duracion': "40 min",
        'disponible': True,
        'foto': "bocatoma/img/moto_kayak.jpg",
    },
    {
        'nombre': "Pesca",
        'descripcion': "Pesca deportiva en el río. Incluye caña de pescar y carnada.",
        'precio': 30.00,
        'duracion': "Una caña y carnada",
        'disponible': True,
        'foto': "bocatoma/img/Pescaa.png",
    },
    {
        'nombre': "Fogata Nocturna",
        'descripcion': "Espacio designado para fogata al aire libre bajo las estrellas.",
        'precio': 0.00,
        'duracion': "Nocturna",
        'disponible': True,
        'foto': "bocatoma/img/fogata.jpg",
    },
    {
        'nombre': "Paseo en Caballo",
        'descripcion': "Paseo tranquilo a caballo por las orillas del río.",
        'precio': 150.00,
        'duracion': "30 min",
        'disponible': True,
        'foto': "bocatoma/img/Caballo3.png",
    },
    {
        'nombre': "Natación en el Río",
        'descripcion': "Acceso a las áreas seguras de nado en las aguas cristalinas del río.",
        'precio': 0.00,
        'duracion': "Libre",
        'disponible': True,
        'foto': "bocatoma/img/natacionnn.jpg",
    },
]

for a in actividades_data:
    obj, created = Actividad.objects.update_or_create(
        nombre=a['nombre'],
        defaults=a
    )
    print(f"Actividad: {obj.nombre} - {obj.precio_texto} ({'creada' if created else 'actualizada'})")

# 3. Superusuario de prueba
admin_user, created = User.objects.get_or_create(username='admin')
admin_user.set_password('admin123')
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.email = 'admin@labocatoma.com'
admin_user.first_name = 'Administrador'
admin_user.last_name = 'La Bocatoma'
admin_user.save()
Perfil.objects.get_or_create(usuario=admin_user, defaults={'telefono': '834 274 4432', 'origen': 'Gómez Farías'})
print(f"Superusuario 'admin' listo (contraseña: admin123).")

# 4. Usuario visitante de prueba
visitante, created = User.objects.get_or_create(username='visitante1')
visitante.set_password('bocatoma2026')
visitante.email = 'visitante1@ejemplo.com'
visitante.first_name = 'Juan'
visitante.last_name = 'Pérez'
visitante.save()
Perfil.objects.get_or_create(usuario=visitante, defaults={'telefono': '834 111 2233', 'origen': 'Ciudad Victoria'})
print(f"Usuario visitante 'visitante1' listo (contraseña: bocatoma2026).")

print("--- Datos iniciales listos con éxito ---")
