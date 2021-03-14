DEBUG = True

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

#config for models.py
DB_NAME = 'programming_forum'
DB_USER = 'postgres'
DB_PASSWORD = ''
DB_HOST = '127.0.0.1'
DB_PORT = '5432'
