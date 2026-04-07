from django.db import transaction
from rest_framework import serializers

from . import models
from .tasks import send_order_confirmation_email


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    featured_product = serializers.StringRelatedField()

    class Meta:
        model = models.Collection
        fields = ["id", "title", "products_count", "featured_product"]


class ProductImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return models.ProductImage.objects.create(
            product_id=self.context["product_id"], **validated_data
        )

    class Meta:
        model = models.ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "inventory",
            "collection",
            "images",
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
        if self.context["method"] == "POST":
            return 0

        if not hasattr(cart, "item") or not cart.items.exists():
            return 0

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


class CostumerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Costumer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = models.OrderItem
        fields = ["id", "product", "unite_price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    costumer = serializers.StringRelatedField(read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = models.Order
        fields = ["id", "costumer", "payment_status", "placed_at", "items"]


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ["payment_status"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        if not models.Cart.objects.filter(pk=value):
            raise serializers.ValidationError("No cart with the given ID was found!")
        if models.CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError("The cart is empty!")
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]

            costumer = models.Costumer.objects.get(user_id=self.context["user_id"])
            order = models.Order.objects.create(costumer=costumer)

            cart_items = models.CartItem.objects.prefetch_related("product").filter(
                cart_id=cart_id
            )
            order_items = [
                models.OrderItem(
                    quantity=item.quantity,
                    unite_price=item.product.price,
                    order=order,
                    product=item.product,
                )
                for item in cart_items
            ]

            models.OrderItem.objects.bulk_create(order_items)
            models.Cart.objects.filter(pk=cart_id).delete()

            transaction.on_commit(lambda: send_order_confirmation_email.delay(order.id))

            return order
