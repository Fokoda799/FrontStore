from django.urls import path

from .views import CreatePaymentIntentView, checkout_view, confirm_order, stripe_webhook

app_name = "payment"


urlpatterns = [
    path("checkout/", checkout_view, name="checkout"),
    path(
        "create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
    path("confirm-order/", confirm_order, name="confirm-order"),
    path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
]
