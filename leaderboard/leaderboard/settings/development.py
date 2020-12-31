from os import path
from . import *  # pylint: disable=unused-import,wildcard-import

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


INSTALLED_APPS += [  # noqa
    'apps.devapp',  # includes some useful development commands
    'debug_toolbar'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
] + MIDDLEWARE  # noqa


def custom_show_toolbar(_):
    return True  # Always show toolbar in development, regardless of host


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

STATICFILES_DIRS = (
    path.join(BASE_DIR, '../../client/dist'),  # noqa
)

WEBPACK_LOADER['DEFAULT']['CACHE'] = False  # noqa
