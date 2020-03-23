import uuid

from django.db import models
from django.urls import reverse
from django.conf import settings

from .signals import receive_shopify_webhook


class WebHookManager(models.Manager):
    pass
    

class WebHook(models.Model):
    WEBHOOKS_TOPICS = (
        ("carts/create","carts/create"),
        ("carts/update","carts/update"),
        ("checkouts/create","checkouts/create"),
        ("checkouts/update","checkouts/update"),
        ("checkouts/delete","checkouts/delete"),
        ("collections/create","collections/create"),
        ("collections/update","collections/update"),
        ("collections/delete","collections/delete"),
        ("collection_listings/add","collection_listings/add"),
        ("collection_listings/update","collection_listings/update"),
        ("collection_listings/remove","collection_listings/remove"),
        ("customers/create","customers/create"),
        ("customers/disable","customers/disable"),
        ("customers/enable","customers/enable"),
        ("customers/update","customers/update"),
        ("customers/delete","customers/delete"),
        ("customer_groups/create","customer_groups/create"),
        ("customer_groups/update","customer_groups/update"),
        ("customer_groups/delete","customer_groups/delete"),
        ("draft_orders/create","draft_orders/create"),
        ("draft_orders/update","draft_orders/update"),
        ("draft_orders/delete","draft_orders/delete"),
        ("fulfillments/create","fulfillments/create"),
        ("fulfillments/update","fulfillments/update"),
        ("fulfillment_events/create","fulfillment_events/create"),
        ("fulfillment_events/delete","fulfillment_events/delete"),
        ("inventory_items/create","inventory_items/create"),
        ("inventory_items/update","inventory_items/update"),
        ("inventory_items/delete","inventory_items/delete"),
        ("inventory_levels/connect","inventory_levels/connect"),
        ("inventory_levels/disconnect","inventory_levels/disconnect"),
        ("inventory_levels/update","inventory_levels/update"),
        ("locations/create","locations/create"),
        ("locations/update","locations/update"),
        ("locations/delete","locations/delete"),
        ("orders/cancelled","orders/cancelled"),
        ("orders/create","orders/create"),
        ("orders/fulfilled","orders/fulfilled"),
        ("orders/paid","orders/paid"),
        ("orders/partially_fulfilled","orders/partially_fulfilled"),
        ("orders/updated","orders/updated"),
        ("orders/delete","orders/delete"),
        ("orders/edited","orders/edited"),
        ("order_transactions/create","order_transactions/create"),
        ("products/create","products/create"),
        ("products/update","products/update"),
        ("products/delete","products/delete"),
        ("product_listings/add","product_listings/add"),
        ("product_listings/update","product_listings/update"),
        ("product_listings/remove","product_listings/remove"),
        ("refunds/create","refunds/create"),
        ("app/uninstalled","app/uninstalled"),
        ("shop/update","shop/update"),
        ("locales/create","locales/create"),
        ("locales/update","locales/update"),
        ("tender_transactions/create","tender_transactions/create"),
        ("themes/create","themes/create"),
        ("themes/publish","themes/publish"),
        ("themes/update","themes/update"),
        ("themes/delete","themes/delete"),
    )
    auth_shop = models.ForeignKey(
        "shopify_framework.AuthShop", on_delete=models.CASCADE)
    topic = models.CharField(default="", max_length=50, choices=WEBHOOKS_TOPICS)
    uuid = models.UUIDField(default=uuid.uuid4)
    rest_id = models.BigIntegerField(default=0, blank=True)

    objects = WebHookManager()

    @property
    def hook_url(self):
        reverse_args = {"webhook_uuid":self.uuid}
        url = "{}{}".format(
            settings.SHOPIFY_FRAMEWORK_APP_ROOT_URL,
            reverse(
                'shopify_framework:webhook_dispatcher', kwargs=reverse_args))
        return url

    def delete(self, *args, **kwargs):
        self.delete_remote()
        return super(WebHook, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if not self.pk and not self.rest_id:
            response = self.create_remote()
            if response.status_code != 201:
                message = f"{self.topic} not allowed by the scopes registered"
                raise Exception(message)
            else:
                self.rest_id = response.json()['webhook']['id']

        return super(WebHook, self).save(*args, **kwargs)

    def create_remote(self):
        data = {
            "webhook": {
                "topic": self.topic,
                "address": self.hook_url,
                "format": "json"
                }
            }

        return self.auth_shop.remote.post(
            '/admin/api/2020-01/webhooks.json', data)

    def delete_remote(self):
        return self.auth_shop.remote.delete(
            f'/admin/api/2020-01/webhooks/{self.rest_id}.json')

    def update_remote(self):
        print("UPDATE")

    def run(self, data):
        receive_shopify_webhook.send(
            sender=self.__class__, auth_shop=self.auth_shop,
            topic=self.topic, data=data)
    
    def __str__(self):
        return self.topic
    
        