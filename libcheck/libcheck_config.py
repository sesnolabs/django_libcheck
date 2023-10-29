DEFAULT_URL = 'https://libcheck.sesnolabs.net/v1/resilience/django_libcheck'
DEFAULT_LIBRARIES = [
    'django', 'os', 'sys',  # default Django libraries
    'setuptools', 'warnings', 'requests',  # libcheck necessary libraries
]
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
