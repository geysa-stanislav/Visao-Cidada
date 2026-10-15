import os
from pathlib import Path

# Configuração Base
BASE_DIR = Path(__file__).resolve().parent.parent

# CHAVE DE SEGURANÇA (Necessária para o Django iniciar)
CHAVE_ARQUIVO = '/home/VisaoCidada/secret_key.txt'
if os.path.exists(CHAVE_ARQUIVO):
    # Servidor: chave lida de um arquivo fora do projeto e modo de producao
    with open(CHAVE_ARQUIVO) as f:
        SECRET_KEY = f.read().strip()
    DEBUG = False
else:
    # Computador local: chave so de testes e modo de desenvolvimento
    SECRET_KEY = 'chave-apenas-para-testes-locais'
    DEBUG = True
ALLOWED_HOSTS = ['visaocidada.pythonanywhere.com', 'localhost', '127.0.0.1']
# Aplicações instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'painel',
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

ROOT_URLCONF = 'hackathon_ufms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hackathon_ufms.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'painel' / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# REDIRECIONAMENTOS DE AUTENTICAÇÃO (SaaS)
LOGOUT_REDIRECT_URL = 'index'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# CHAVE DO GROQ (Onde a mágica acontece)
OPENAI_API_KEY = ""
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'
