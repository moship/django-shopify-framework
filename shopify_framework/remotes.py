import requests
import json

class AuthShopRemote(object):

    def __init__(self, subdomain, access_token):
        self.subdomain = subdomain
        self.access_token = access_token
    
    def post(self, path, data):
        return requests.post(
            f"{self.shopify_url}{path}",
            data=json.dumps(data),
            headers=self.headers
        )

    def put(self, path, data):
        return requests.put(
            f"{self.shopify_url}{path}",  
            data=json.dumps(data),
            headers=self.headers
            )

    def get(self, path):
        return requests.get(
            f"{self.shopify_url}{path}",  
            headers=self.headers
        )

    def delete(self, path):
        return requests.delete(
            f"{self.shopify_url}{path}",  
            headers=self.headers
        )
    
    def graph(self, query, variables=None, version="2020-01"):
        
        url = f"{self.shopify_url}/admin/api/{version}/graphql.json"
        data = {"query": query}
        if variables:
            data["variables"] = variables
        return requests.post(url, headers=self.headers, json=data)

    @property
    def headers(self):
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }
        return headers

    @property
    def shopify_url(self):
        return f"https://{self.subdomain}.myshopify.com"