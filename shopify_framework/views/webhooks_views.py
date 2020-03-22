import json

from django.views import View
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import WebHook

@csrf_exempt
def webhook_dispatcher(request, webhook_uuid):
    webhook = WebHook.objects.get(uuid=webhook_uuid)
    if webhook.auth_shop.webhook_is_authenticated(request):
        webhook.run(json.loads(request.body))
    return HttpResponse()
