from os import path
from . import *  # pylint: disable=unused-import

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


INSTALLED_APPS += [  # noqa
    'debug_toolbar'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
] + MIDDLEWARE  # noqa


def custom_show_toolbar(request):
    return True  # Always show toolbar in development, regardless of host


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

STATICFILES_DIRS = (
    path.join(BASE_DIR, '../../client/dist'),  # noqa
)

WEBPACK_LOADER['DEFAULT']['CACHE'] = False  # noqa
