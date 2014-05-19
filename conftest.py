import os
import logging

from django.conf import settings

from oscar import OSCAR_MAIN_TEMPLATE_DIR, get_core_apps

location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x
)
sandbox = lambda x: location("sandbox/%s" % x)

logging.basicConfig(level=logging.INFO)


def pytest_configure():
    from oscar.defaults import OSCAR_SETTINGS
    from oscar_mws.defaults import OSCAR_MWS_SETTINGS

    DEFAULT_SETTINGS = OSCAR_SETTINGS
    DEFAULT_SETTINGS.update(OSCAR_MWS_SETTINGS)
    DEFAULT_SETTINGS['OSCAR_DEFAULT_CURRENCY'] = 'USD'

    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        USE_TZ=True,
        MEDIA_ROOT=sandbox('public/media'),
        MEDIA_URL='/media/',
        STATIC_URL='/static/',
        STATICFILES_DIRS=[
            sandbox('static/')
        ],
        STATIC_ROOT=sandbox('public'),
        STATICFILES_FINDERS=(
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            'compressor.finders.CompressorFinder',
        ),
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.request",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.contrib.messages.context_processors.messages",
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'oscar.apps.basket.middleware.BasketMiddleware',
        ),
        ROOT_URLCONF='sandbox.sandbox.urls',
        TEMPLATE_DIRS=[
            sandbox('templates'),
            OSCAR_MAIN_TEMPLATE_DIR,
        ],
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.flatpages',
            'django.contrib.admin',

            'compressor',
            'south',

            'oscar_mws',
        ] + get_core_apps(),
        AUTHENTICATION_BACKENDS=(
            'django.contrib.auth.backends.ModelBackend',
        ),
        COMPRESS_ENABLED=True,
        COMPRESS_OFFLINE=False,
        COMPRESS_PRECOMPILERS=(
            ('text/less', 'lessc {infile} {outfile}'),
        ),
        LOGIN_REDIRECT_URL='/accounts/',
        APPEND_SLASH=True,
        SITE_ID=1,
        HAYSTACK_CONNECTIONS={
            'default': {
                'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
            },
        },
        LOGGING={
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                },
                'simple': {
                    'format': '%(levelname)s %(message)s'
                },
            },
            'filters': {
                'require_debug_false': {
                    '()': 'django.utils.log.RequireDebugFalse'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                }
            },
            'loggers': {
                'oscar_mws': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
                'oscar_mws.api': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
                'django.request': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
            }
        },
        DEBUG=True,
        **DEFAULT_SETTINGS
    )
