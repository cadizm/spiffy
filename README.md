
 1. `$ mkdir spiffy`
 2. `$ cd spiffy`
 3. `$ git init .`
 4. `$ mkvirtualenv spiffy`
 5. `$ pip install -r requirements.txt`
 6. `$ django-admin startproject spiffy`
 7. `$ add2virtualenv spiffy`
 8. `mkdir bin && touch bin/runserver.py`
 9. `$ python bin/runserver.py`
10. `$ python manage.py makemigrations`
11. `$ python manage.py migrate`
12. `$ python manage.py startapp profile`
13. `$ python manage.py startapp api`

### Helper start server

```
# bin/runserver.py

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'spiffy.settings'

import django
django.setup()

from django.core import management
management.call_command('runserver', '127.0.0.1:8001')
```

### Additions to default settings

```
# settings.py

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/spiffy.log',
            'formatter': 'verbose',
        }

    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'spiffy': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

INSTALLED_APPS = [
    ...
    'django_extensions',
    'profile',
    'api',
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

ELASTICSEARCH_CONFIG = {
    'hosts': [
        'localhost:9200'
    ],
    'sniff_on_connection_fail': True,
    'sniff_timeout': 3,
    'timeout': 5
}
```
