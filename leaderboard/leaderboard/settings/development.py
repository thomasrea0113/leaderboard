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

INTERNAL_IPS = [
    '127.0.0.1'
]

WEBPACK_LOADER['DEFAULT']['CACHE'] = False  # noqa
WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = path.join(BASE_DIR, '../../client/dist/webpack-stats.json')  # noqa
