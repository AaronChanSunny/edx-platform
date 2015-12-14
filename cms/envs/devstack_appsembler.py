# devstack_appsembler.py

from .devstack import *
from .appsembler import *

INSTALLED_APPS += ('appsembler_lms',)
# TEMPLATE_CONTEXT_PROCESSORS += ('appsembler.context_processors.intercom',)

FEATURES['APPSEMBLER_SECRET_KEY'] = "secret_key"
OAUTH_ENFORCE_SECURE = False

