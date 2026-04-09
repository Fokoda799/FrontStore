import json

import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout_view(request):
    payment_amount = request.GET.get("amount", 1000)
    return render(
        request,
        "checkout.html",
        {
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "payment_amount": payment_amount,
        },
    )


def confirm_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    return JsonResponse({"status": "confirmed"})


class CreatePaymentIntentView(APIView):
    def post(self, request):
        try:
            # So $29.99 becomes 2999
            amount = request.data.get("amount")

            if amount is None:
                return Response(
                    {"error": "amount is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=settings.CURRENCY,
                # You can attach metadata to link this payment to your order
                metadata={"user_id": 1},
            )

            # Return the client_secret — the frontend needs this to complete the payment
            return Response({"client_secret": intent.client_secret})

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    # Step 1 — Verify the signature using the raw bytes
    # This confirms the request genuinely came from Stripe
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # Step 2 — Parse the same raw bytes as a plain Python dict
    # We use this instead of the StripeObject because regular dicts support .get()
    event_dict = json.loads(payload)

    # Step 3 — Handle events using event_dict for data access
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event_dict["data"]["object"]  # plain dict, .get() works fine
        metadata = payment_intent.get("metadata") or {}
        user_id = metadata.get("user_id")

        # TODO: fulfill the order here
        print(f"Payment succeeded for user_id={user_id}")

    elif event["type"] == "payment_intent.payment_failed":
        # TODO: notify user, release reserved inventory, etc.
        pass

    return HttpResponse(status=200)
