from django.urls import path

from .views import (
    CreatePaymentIntentView,
    PaymentStatusView,
    checkout_view,
    stripe_webhook,
    thank_you_view,
)

app_name = "payment"


urlpatterns = [
    path("checkout/", checkout_view, name="checkout"),
    path("thank-you/", thank_you_view, name="thank-you"),
    path(
        "create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
    path("status/", PaymentStatusView.as_view(), name="payment-status"),
    path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
]
