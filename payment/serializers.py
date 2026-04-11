from rest_framework import serializers


class CreatePaymentIntentSerializer(serializers.Serializer):

    # We restrict object_type to known values so nothing unexpected gets stored
    content_type = serializers.ChoiceField(
        choices=["order", "subscription", "donation"]
    )

    # Must be a real positive ID
    object_id = serializers.IntegerField(min_value=1)
