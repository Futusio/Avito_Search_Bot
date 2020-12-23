import logging


class Filter(logging.Filter):
    def filter(self, record):
        if record.levelname == 'WARNING' or record.levelname == 'CRITICAL':
            return False
        return True


logger_config = {
    'version': 1, 
    'disable_existing_loggers': False,
# Formatters 
    'formatters': {
        'file_format': {
            'format': '{asctime}:[{levelname}] - {name} | {message}',
            'style': '{'
        },
        'std_format':{
            'format': '[{levelname}] {message} || By {name}',
            'style': '{'
        },
        'errors':{
            'format':'{asctime}: [{levelname}] | Module: {module}.py | Function {funcName}() has message on {lineno} line\n\tMessage: {message}',
            'style': '{'
        }
    },
# Handlers
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format',
        },
        'file':{
            'class': 'logging.FileHandler',
            'filename': 'logs.log',
            'level':'INFO',
            'formatter':'file_format',
            'filters': ['one_filter',]
        },
        'critical':{
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'level':'WARNING',
            'formatter':'errors',
        }
    },
# Loggers 
    'loggers': {
        'bot': {
            'level': 'DEBUG',
            'handlers':['console','file', 'critical']
        }, 
        'web': {
            'level': 'DEBUG',
            'handlers':['console', 'file', 'critical']
        }
    },
# Filters
    'filters': {
        'one_filter': {
            '()': Filter,
        }
    }
}