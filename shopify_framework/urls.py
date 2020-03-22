from django.contrib import admin
from django.urls import path


from . import views

app_name="shopify_framework"

urlpatterns = [
    path( 'webhooks/<uuid:webhook_uuid>/', views.webhook_dispatcher, 
          name="webhook_dispatcher"),
]