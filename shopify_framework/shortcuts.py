from django.shortcuts import HttpResponse, render
from .models import AuthShop

def oauth_redirect(request, shop_url ):
    """Redirect to authorization page"""
    auth_shop = AuthShop.objects.get_by_shop_url(shop_url)
    context = {"shop":auth_shop}
    return render(request, 'shopify_framework/auth_redirect.html', context) 