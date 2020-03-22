import createApp from "@shopify/app-bridge";
import { Redirect } from "@shopify/app-bridge/actions";

const shopOrigin = window.shopOrigin;
const apiKey = window.apiKey;
const permissionUrl = window.permissionUrl;

if (window.top == window.self) {
  window.location.assign(`https://${shopOrigin}/admin${permissionUrl}`);
} else {
  const app = createApp({
    apiKey: apiKey,
    shopOrigin: shopOrigin
  });
  const redirect = Redirect.create(app);
  redirect.dispatch(Redirect.Action.ADMIN_PATH, permissionUrl);
}
