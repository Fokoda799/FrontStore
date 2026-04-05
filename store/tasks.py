import random
import string
import uuid
from decimal import Decimal

from celery import shared_task
from django.db import models
from django.utils import timezone

from .models import Product


def _random_text(prefix: str = "Product", size: int = 8) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=size))
    return f"{prefix} {suffix}"


def _random_value_for_field(field: models.Field):
    if isinstance(field, (models.CharField, models.SlugField)):
        max_len = getattr(field, "max_length", 50) or 50
        return _random_text(size=min(10, max_len))[:max_len]

    if isinstance(field, models.TextField):
        return f"{_random_text()} description"

    if isinstance(field, models.DecimalField):
        digits = max(1, field.max_digits - field.decimal_places)
        max_int = min(10**digits - 1, 9999)
        value = random.uniform(1, max_int)
        return Decimal(str(round(value, field.decimal_places)))

    if isinstance(field, models.FloatField):
        return round(random.uniform(1, 9999), 2)

    if isinstance(field, (models.IntegerField, models.BigIntegerField)):
        return random.randint(1, 9999)

    if isinstance(
        field, (models.PositiveIntegerField, models.PositiveSmallIntegerField)
    ):
        return random.randint(1, 9999)

    if isinstance(field, models.BooleanField):
        return random.choice([True, False])

    if isinstance(field, models.DateTimeField):
        return timezone.now()

    if isinstance(field, models.DateField):
        return timezone.now().date()

    if isinstance(field, models.UUIDField):
        return uuid.uuid4()

    return None


@shared_task
def create_random_product():
    """
    Celery task: creates one random Product row and saves it to the database.
    Works best when Product has standard field types.
    """
    data = {}

    for field in Product._meta.get_fields():
        if not isinstance(field, models.Field):
            continue
        if field.auto_created or field.primary_key:
            continue
        if field.has_default():
            continue
        if getattr(field, "null", False):
            continue

        if isinstance(field, models.ForeignKey):
            related_qs = field.remote_field.model.objects.all()
            if not related_qs.exists():
                return {
                    "created": False,
                    "reason": f"Missing related objects for required FK '{field.name}'",
                }
            data[field.name] = related_qs.order_by("?").first()
            continue

        value = _random_value_for_field(field)
        if value is not None:
            data[field.name] = value

    product = Product.objects.create(**data)
    return {"created": True, "product_id": product.pk}
