import django.dispatch

receive_shopify_webhook = django.dispatch.Signal(
    providing_args=["auth_shop", "topic", "data"])