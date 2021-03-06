"""
Django settings for gogo project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+xtgn6s8(15e#nv)1v5ta7n)*fpt=xq7+gt5o_28$8lzg3=ccm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = ['localhost', '159.203.190.248',]


ADMINS = (
    ('Jose Andrade', 'avarajame@gmail.com'),
)


# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'analisis',
	'colaboradores',
	'cuestionarios',
	'mensajeria',
	'usuarios',
	'colaboradores_360',
	'cuestionarios_360',
	'mensajeria_360',
	'redes_360',
	'mptt',
	#'debug_toolbar',
	'exp_usuario',
	'entornoPruebas',
	'daterange_filter',

)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'gogo.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS':[BASE_DIR+'/administrar/plantillas/',
				BASE_DIR+'/analisis/plantillas/',
				BASE_DIR+'/colaboradores/plantillas/',
				BASE_DIR+'/cuestionarios/plantillas/',
				BASE_DIR+'/mensajeria/plantillas/',
				BASE_DIR+'/usuarios/plantillas/',
				BASE_DIR+'/cuestionarios_360/plantillas/',
				BASE_DIR+'/mensajeria_360/plantillas/',
				BASE_DIR+'/colaboradores_360/plantillas/',
				BASE_DIR+'/redes_360/plantillas/',
				BASE_DIR+'/exp_usuario/plantillas',
				BASE_DIR+'/entornoPruebas/plantillas',],
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

WSGI_APPLICATION = 'gogo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
	'default': {

			# 'ENGINE':'django.db.backends.sqlite3',
			# 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
			'NAME': 'gogo_db',

			# 'USER': 'usuariodb_gogo',
			# 'PASSWORD':'W#y2d@uV4+eSPuwrEc$UTrE4eCruTHas',
			'HOST':'127.0.0.1',
			# 'HOST':'networksdb.co3mxnuop6eu.us-east-1.rds.amazonaws.com',


			'USER': 'user_gogo_db',
			'PASSWORD': 'pass_db_gogo_#asdf',


			# 'PORT':'5432',

			# master PASSWORD
			#'USER': 'suidi',
			#'PASSWORD':'Networks123*',


	}
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-CO'

TIME_ZONE = 'America/Bogota'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + 'static'
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, "static"),
)

MEDIA_URL  = '/media/'
MEDIAFILES_DIRS = (
	os.path.join(BASE_DIR, "media"),
)
MEDIA_ROOT = BASE_DIR + '/media/'
# secure proxy SSL header and secure cookies
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# session expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# CACHES = {
# 	 'default': {
# 		 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
# 		 'LOCATION': BASE_DIR,
# 	 }
# }



# CACHES = {
#  	'default':{
#  		'BACKEND':'redis_cache.RedisCache',
#  		'LOCATION':'127.0.0.1:6379',
#  		'OPTIONS':{
#  			'DB':2,
#  			'PASSWORD':'frec5epEbucHene27E4re6uspuT7ayus'
#  		},
#  	},
# }

#
#
CACHES = {
 	'default':{
 		'BACKEND':'redis_cache.RedisCache',
 		'LOCATION':'127.0.0.1:6379',
 		# 'OPTIONS':{
 		# 	'DB':2,
 		# 	'PASSWORD':'frec5epEbucHene27E4re6uspuT7ayus'
 		# },
 	},
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
