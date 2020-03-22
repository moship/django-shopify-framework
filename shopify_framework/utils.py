# Django
from django.conf import settings

# Utilities
from cryptography.fernet import Fernet

def decrypt(item):
    key = settings.SHOPIFY_FRAMEWORK_AUTH_SECRET.encode("utf-8")
    f = Fernet(key)
    return f.decrypt(item.encode("utf-8")).decode("utf-8")


def encrypt(item):
    key = settings.SHOPIFY_FRAMEWORK_AUTH_SECRET.encode("utf-8")
    f = Fernet(key)
    return f.encrypt(item.encode("utf-8")).decode("utf-8")