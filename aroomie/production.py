from aroomie.settings import *

DEBUG = False

APP_NAME = os.environ.get('APP_NAME', 'aroomie')
ALLOWED_HOSTS = ['%s.herokuapp.com' % APP_NAME]
