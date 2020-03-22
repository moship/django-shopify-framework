========================
Django Shopify Framework
========================

Shopify Framework is a Django app that help you create an embed app.
use Django sessions to store the authenticated app, help you create 
and authenticate Web Hooks and give you an interface to interact with
the Rest Api or the Graph Api resources.

Quick start
-----------

1. Add this information to your settings.py file::

    SHOPIFY_FRAMEWORK_AUTH_SECRET=""
    SHOPIFY_FRAMEWORK_APP_API_KEY=""
    SHOPIFY_FRAMEWORK_APP_API_SECRET_KEY=""
    SHOPIFY_FRAMEWORK_APP_ROOT_URL=""
    SHOPIFY_FRAMEWORK_APP_REDIRECT_URL=""
    SHOPIFY_FRAMEWORK_APP_SCOPES=[
        ...scopes required,
    ]

    SESSION_COOKIE_SAMESITE=None