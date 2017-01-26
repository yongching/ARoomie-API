from aroomie.settings import *

DEBUG = True

ALLOWED_HOSTS = []

PUSH_NOTIFICATIONS_SETTINGS = {
    "APNS_CERTIFICATE": os.environ['APNS_CERTIFICATE'],
}
