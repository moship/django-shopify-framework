from django.contrib import admin

from .models import AuthShop, WebHook

class WebHookInline(admin.TabularInline):
    model = WebHook
    extra = 0


@admin.register(AuthShop)
class Admin(admin.ModelAdmin):
    '''Admin View for AuthShop'''
    inlines=[WebHookInline,]

@admin.register(WebHook)
class Admin(admin.ModelAdmin):
    '''Admin View for WebHook'''
    pass
