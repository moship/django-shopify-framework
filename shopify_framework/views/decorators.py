from functools import wraps
from ..models import AuthShop, AnonymousShop

def embed_view(view_func):
    """
    Add the Content-Security-Policy frame-ancestors that allow this view to 
    be embed in a shopify admin iframe
    """

    def is_shop_authenticated(request):
        SHOP_KEY = 'shopify_framework_shop'
        CODE_KEY = 'shopify_framework_code'

        if 'code' in request.GET:

            shop = AuthShop.objects.get_by_shop_url(shop=request.GET['shop'])
            stored_code = request.session.get(CODE_KEY)
            received_code = request.GET.get('code', 'no-code')

            if stored_code == received_code and request.session.get(SHOP_KEY):

                shop = AuthShop.objects.get(subdomain=request.session[SHOP_KEY])
                return shop, True

            elif shop.code_is_valid(request):
                request.session[SHOP_KEY] = shop.subdomain
                request.session[CODE_KEY] = request.GET['code']
                return shop, True

        elif 'shop' in request.GET:
            
            shop = AuthShop.objects.get_by_shop_url(shop=request.GET['shop'])

            if shop.subdomain == request.session.get(SHOP_KEY):
                return shop, True
        
        elif 'shop' not in request.GET:
            if request.session.get(SHOP_KEY):
                shop = AuthShop.objects.get(subdomain=request.session[SHOP_KEY])
                return shop, True

        request.session.flush()
        return AnonymousShop, False

    def wrapped_view(request, **kwargs):

        # Check if the request is made from a new shopify admin session, 
        # an installation link or the shop is already authenticated
        
        shop, is_authenticated = is_shop_authenticated(request)
        
        shop.is_authenticated = is_authenticated
        request.auth_shop = shop

        resp = view_func(request, **kwargs)

        resp['Content-Security-Policy'] = 'frame-ancestors *.myshopify.com'
        
        return resp
    
    return wraps(view_func)(wrapped_view)

    