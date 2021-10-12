import logging


DB_NAME = "test.db"

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': "[%(asctime)s] [%(levelname)s] - %(name)s: %(message)s",
        },
    },

    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'operators.log',
        },
    },
    'loggers': {
        'operators': {
            'handlers': ['file', ],
            'level': logging.DEBUG
        },
    },
}