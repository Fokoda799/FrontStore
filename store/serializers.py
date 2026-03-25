from decimal import Decimal

from rest_framework import serializers

from . import models


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    featured_product = serializers.StringRelatedField()

    class Meta:
        model = models.Collection
        fields = ["id", "title", "products_count", "featured_product"]


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(
        method_name="calculate_tax", read_only=True
    )
    collection = serializers.StringRelatedField(read_only=True)

    def calculate_tax(self, product):
        return product.price * Decimal(1.1)

    class Meta:
        model = models.Product
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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ["id", "name", "text", "date"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return models.Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["id", "title", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name="calc_total_price", read_only=True
    )

    def calc_total_price(self, item: models.CartItem):
        return item.product.price * item.quantity

    class Meta:
        model = models.CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name="calc_total_price", read_only=True
    )

    def calc_total_price(self, cart):
        return sum(item.quantity * item.product.price for item in cart.items.all())

    class Meta:
        model = models.Cart
        fields = ["id", "items", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with given the ID was found!")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            item = models.CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            item.quantity += quantity
            item.save()
            self.instance = item
        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    class Meta:
        model = models.CartItem
        fields = ["id", "product_id", "quantity"]
