from .base import *

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'thepattern',
        'PORT': 3306,
        'USER':'root',
        'PASSWORD':'',
        'HOST':'http://127.0.0.1:8000'
    }
}