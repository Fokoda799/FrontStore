from decimal import Decimal

from rest_framework import serializers

from .models import Collection, Product


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField()
    featured_product = serializers.StringRelatedField()

    class Meta:
        model = Collection
        fields = ["id", "title", "products_count", "featured_product"]


class ProductSerializers(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    # collection = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "inventory",
            "price_with_tax",
            "collection",
        ]

    def calculate_tax(self, product):
        return product.price * Decimal(1.1)
