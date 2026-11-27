
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# Clave secreta (en producción se puede sobreescribir con variable de entorno)
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-2lr=l!lmpnd70=sq=s-lxk8az+^blzwo97@gh2=4ekcv!@pgw1'
)

# Cargar variables desde archivo .env si existe (usando biblioteca estándar de Python)
env_file = BASE_DIR / '.env'
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if v:
                    os.environ[k] = v


# DEBUG activado para desarrollo, en producción desactivar con env var
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Hosts permitidos (acepta cualquier host para facilitar pruebas y PythonAnywhere)
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bocatoma',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MiSitio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MiSitio.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# Validación amigable para visitantes escolares y turistas:
# - No permite contraseñas similares a datos de usuario (nombre/usuario)
# - Requiere una longitud mínima básica de 6 caracteres
# - No bloquea innecesariamente por complejidad extrema
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Redirecciones de autenticación
LOGIN_URL = 'bocatoma:login'
LOGIN_REDIRECT_URL = 'bocatoma:mis_reservaciones'
LOGOUT_REDIRECT_URL = 'bocatoma:inicio'


# Configuración de Correo Electrónico
# Si se configuran usuario y contraseña de Gmail en el archivo .env,
# activa automáticamente el envío real por SMTP.
# De lo contrario, imprime en la consola del servidor (modo desarrollo seguro).
if os.getenv('EMAIL_HOST_USER') and os.getenv('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = os.getenv(
        'DJANGO_EMAIL_BACKEND',
        'django.core.mail.backends.smtp.EmailBackend'
    )
else:
    EMAIL_BACKEND = os.getenv(
        'DJANGO_EMAIL_BACKEND',
        'django.core.mail.backends.console.EmailBackend'
    )

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

if EMAIL_HOST_USER:
    DEFAULT_FROM_EMAIL = f'Parque La Bocatoma <{EMAIL_HOST_USER}>'
else:
    DEFAULT_FROM_EMAIL = 'Parque La Bocatoma <labocatoma.ecoturismo@gmail.com>'

