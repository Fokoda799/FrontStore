import json

import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import CreatePaymentIntentSerializer
from .signals import payment_failed, payment_succeeded
from .utils import get_payable_model, get_payment_content_type

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        object_id = serializer.validated_data["object_id"]
        content_type = get_payment_content_type()
        PayableModel = get_payable_model()

        # Gate 1 — reuse existing pending intent if one already exists
        existing_payment = Payment.objects.filter(
            content_type=content_type,
            object_id=object_id,
            status=Payment.PAYMENT_STATUS_PENDING,
        ).first()

        if existing_payment:
            intent = stripe.PaymentIntent.retrieve(existing_payment.stripe_intent_id)
            return Response({"client_secret": intent.client_secret})

        # Gate 2 — verify the object exists
        obj = PayableModel.objects.filter(id=object_id).first()

        if not obj:
            return Response({"error": "Not found"}, status=404)

        # Gate 3 — verify ownership and payable state via mixin convention
        if not obj.is_payable_by(request.user):
            return Response({"error": "Not found or not payable"}, status=404)

        # Gate 4 — verify this object requires online payment at all
        if not obj.requires_online_payment:
            return Response(
                {"error": "This order does not require online payment"}, status=400
            )

        # Gate 5 — compute amount server-side and enforce minimum
        amount = int(obj.total_amount * 100)

        if amount < 50:
            return Response(
                {"error": "Order total is below the minimum chargeable amount"},
                status=400,
            )

        # All gates passed — safe to create the intent
        try:
            with transaction.atomic():
                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency=settings.PAYMENT_CURRENCY,
                    metadata={
                        "object_id": str(object_id),
                        "user_id": str(request.user.id),
                    },
                )
                Payment.objects.create(
                    stripe_intent_id=intent.id,
                    user=request.user,
                    content_type=content_type,
                    object_id=object_id,
                    amount=amount,
                    currency=settings.PAYMENT_CURRENCY,
                    status=Payment.PAYMENT_STATUS_PENDING,
                )

            return Response({"client_secret": intent.client_secret})

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── Payment Status (polled by frontend) ─────────────────────────────────────


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stripe_intent_id = request.query_params.get("payment_intent")

        if not stripe_intent_id:
            return Response({"error": "Missing payment_intent"}, status=400)

        try:
            payment = Payment.objects.get(
                stripe_intent_id=stripe_intent_id, user=request.user
            )
        except Payment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        return Response(
            {
                "status": payment.status,
                "object_id": payment.object_id,
                "amount": payment.amount,
            }
        )


# ─── Stripe Webhook ───────────────────────────────────────────────────────────


@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    event_dict = json.loads(payload)
    payment_intent = event_dict["data"]["object"]
    stripe_intent_id = payment_intent["id"]

    if event["type"] == "payment_intent.succeeded":
        Payment.objects.filter(stripe_intent_id=stripe_intent_id).update(
            status=Payment.PAYMENT_STATUS_SUCCEEDED, stripe_payload=payment_intent
        )
        payment_succeeded.send(
            sender=None,
            stripe_intent_id=stripe_intent_id,
            metadata=payment_intent.get("metadata") or {},
        )

    elif event["type"] == "payment_intent.payment_failed":
        Payment.objects.filter(stripe_intent_id=stripe_intent_id).update(
            status=Payment.PAYMENT_STATUS_FAILED, stripe_payload=payment_intent
        )
        payment_failed.send(
            sender=None,
            payment_intent_id=stripe_intent_id,
            metadata=payment_intent.get("metadata") or {},
        )

    # All other event types are acknowledged silently — no crash
    return HttpResponse(status=200)


# Only for testing!
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


def thank_you_view(request):
    order_id = request.GET.get("order_id")
    return render(request, "thank_you.html", {"order_id": order_id})
