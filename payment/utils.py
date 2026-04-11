from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

app_label, model_name = settings.PAYMENT_PAYABLE_MODEL.rsplit(".", 1)


def get_payable_model():
    """
    Resolves the payable model class from settings.
    e.g. 'store.Order' → the actual Order class.
    This lets the payment app work with any model without importing it directly.
    """
    return apps.get_model(app_label, model_name)


def get_payment_content_type():
    """
    Reads PAYMENT_PAYABLE_MODEL from settings (e.g. 'store.Order') and returns
    the corresponding ContentType. This is the only place in the payment
    app that touches the setting, everything else uses this function.
    """
    return ContentType.objects.get(app_label=app_label, model=model_name.lower())
