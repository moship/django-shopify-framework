import hmac
import base64
import time
import json
import six
from hashlib import sha256

from django.db import models
from django.conf import settings

import requests

from ..remotes import AuthShopRemote
from ..utils import encrypt, decrypt
from ..models.webhook_model import WebHook as WebHookModel

class AuthShopManager(models.Manager):
    def get_by_shop_url(self, shop):
        subdomain = shop.split(".myshopify.com")[0]
        shop, _created = super().get_queryset().get_or_create(
            subdomain=subdomain)
        return shop

class AuthShop(models.Model):
    APP_TYPES = (('public', 'Public'),('custom','Custom'))

    subdomain = models.CharField(default="", max_length=50)
    app_type = models.CharField(
        default="public", max_length=50,choices=APP_TYPES)
    access_token = models.CharField(default="", max_length=200)
    custom_app_api_key = models.CharField(  
        default="", max_length=200, blank=True, null=True)
    custom_app_api_secret_key = models.CharField(
        default="", max_length=200, blank=True, null=True)

    objects = AuthShopManager()

    def __init__(self, *args, **kwargs):

        instance =  super(AuthShop, self).__init__(*args, **kwargs)

        if self.subdomain and self.access_token:
            self.remote = AuthShopRemote(self.subdomain, 
                                         self.get_access_token())

        return instance

    def set_access_token(self, access_token):
        if access_token:
            self.access_token = encrypt(access_token)
            self.save()

    def get_access_token(self):
        return decrypt(self.access_token)

    def get_permission_path(self, scopes=None, access_mode=""):
        if not scopes:
            scopes = settings.SHOPIFY_FRAMEWORK_APP_SCOPES
        
        scopes_str = ""
        scopes_quantity = len(scopes)
        i = 1
        for scope in scopes:
            scopes_str += scope
            if i < scopes_quantity:
                scopes_str += ","
            i += 1

        redirect_uri=settings.SHOPIFY_FRAMEWORK_APP_REDIRECT_URL
        nonce=""
        return "{}{}{}{}".format(
            f"/oauth/authorize?",
            f"client_id={self.get_api_key()}&scope={scopes_str}",
            f"&redirect_uri\={redirect_uri}&state=",
            f"{nonce}&grant_options[]={access_mode}")

    def get_api_key(self):
        if self.app_type == 'custom':
            return decrypt(self.custom_app_api_key)
        else:
            return settings.SHOPIFY_FRAMEWORK_APP_API_KEY

    def get_api_secret(self):
        if self.app_type == 'custom':
            return decrypt(self.custom_app_api_secret_key)
        else:
            return settings.SHOPIFY_FRAMEWORK_APP_API_SECRET_KEY

    def code_is_valid(self, request):
        if self.validate_params(request) and request.GET.get('code'):
            response = self.call_for_access_token(request.GET['code'])

            if response.status_code == 200:
                
                if not self.access_token:
                    self.set_access_token(response.json().get("access_token"))

                return True

        return False
        
    def call_for_access_token(self, code):
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json"
        }
        data = {
            "client_id":self.get_api_key(),
            "client_secret":self.get_api_secret(),
            "code":code
        }
        return requests.post(
            f"https://{self.shopify_url}/admin/oauth/access_token", json=data, 
            headers=headers)

    def validate_params(self, request):

        params = request.GET
        one_day = 24 * 60 * 60

        if int(params.get('timestamp', 0)) < time.time() - one_day:
            return False
        
        return self.validate_hmac(params, self.get_api_secret())

    def webhook_is_authenticated(self, request):
        if request.META.get("HTTP_X_SHOPIFY_HMAC_SHA256"):
            secret = self.get_api_secret()
            data = request.body
            return self.verify_webhook(
                data, request.META.get("HTTP_X_SHOPIFY_HMAC_SHA256"), secret
            )
        return False

    @classmethod
    def verify_webhook(cls, data, hmac_header, secret):

        SECRET = bytes(secret, encoding="utf-8")
        digest = hmac.new(SECRET, data, sha256).digest()
        computed_hmac = base64.b64encode(digest)
        return hmac.compare_digest(computed_hmac, hmac_header.encode("utf-8"))

    @classmethod
    def validate_hmac(cls, params, secret):
   
        if 'hmac' not in params:
            return False

        hmac_calculated = cls.calculate_hmac(params, secret).encode('utf-8')
        hmac_to_verify = params['hmac'].encode('utf-8')

        # Try to use compare_digest() to reduce vulnerability to timing attacks.
        # If it's not available, just fall back to regular string comparison.
        try:
            return hmac.compare_digest(hmac_calculated, hmac_to_verify)
        except AttributeError:
            return hmac_calculated == hmac_to_verify

    @classmethod
    def calculate_hmac(cls, params, secret):
        """
        Calculate the HMAC of the given parameters in line with Shopify's rules for OAuth authentication.
        See http://docs.shopify.com/api/authentication/oauth#verification.
        """
        encoded_params = cls.__encoded_params_for_signature(params)
        # Generate the hex digest for the sorted parameters using the secret.
        return hmac.new(secret.encode(), encoded_params.encode(), sha256).hexdigest()

    @classmethod
    def __encoded_params_for_signature(cls, params):
        """
        Sort and combine query parameters into a single string, excluding those that should be removed and joining with '&'
        """
        def encoded_pairs(params):
            for k, v in six.iteritems(params):
                if k == 'hmac':
                    continue

                if k.endswith('[]'):
                    #foo[]=1&foo[]=2 has to be transformed as foo=["1", "2"] note the whitespace after comma
                    k = k.rstrip('[]')
                    v = json.dumps(list(map(str, v)))

                # escape delimiters to avoid tampering
                k = str(k).replace("%", "%25").replace("=", "%3D")
                v = str(v).replace("%", "%25")
                yield '{0}={1}'.format(k, v).replace("&", "%26")

        return "&".join(sorted(encoded_pairs(params)))

    @property
    def shopify_url(self):
        return f"{self.subdomain}.myshopify.com"

    def create_webhooks(self, webhooks):
        for webhook in webhooks:
            webhook_tuple = (webhook,webhook)
            if webhook_tuple in WebHookModel.WEBHOOKS_TOPICS:
                self.webhook_set.get_or_create(topic=webhook)
    
    def __str__(self):
        return self.subdomain
    
class AnonymousShop(object):
    is_authenticated = False 