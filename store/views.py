from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from django.db.models import Count

from . import models, serializers
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import AdminOrReadOnly


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.annotate(
        products_count=Count("products")
    ).all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = [AdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        collection = self.get_object()
        if collection.products.count() > 0:
            return Response(
                {"error": "There are products associated with this collection"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(collection)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductsViewSet(ModelViewSet):
    queryset = models.Product.objects.select_related("collection").prefetch_related(
        "images"
    )
    serializer_class = serializers.ProductSerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ["title", "description"]
    ordering_fields = ["price"]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.orderitems.count() > 0:
            return Response(
                {"error": "There are order items associated with this product"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(product)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        return models.Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartsViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = serializers.CartSerializer

    def get_queryset(self):
        if self.request.method == "POST":
            return models.Cart.objects.all()
        return models.Cart.objects.prefetch_related("items__product")

    def get_serializer_context(self):
        return {"method": self.request.method}


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return models.CartItem.objects.filter(
            cart_id=self.kwargs["cart_pk"]
        ).select_related("product")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AddCartItemSerializer
        return serializers.CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


class CostumerViewSet(ModelViewSet):
    queryset = models.Costumer.objects.all()
    serializer_class = serializers.CostumerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        costumer = models.Costumer.objects.get(user_id=request.user.id)

        if request.method == "GET":
            serializer = serializers.CostumerSerializer(costumer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = serializers.CostumerSerializer(costumer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return models.Order.objects.prefetch_related("items__product")
        costumer_id = models.Costumer.objects.only("id").get(user_id=user.id)
        return models.Order.objects.prefetch_related("items__product").filter(
            costumer_id=costumer_id
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateOrderSerializer
        if self.request.method == "PATCH":
            return serializers.UpdateOrderSerializer
        return serializers.OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)


class ProductImageViewSet(ModelViewSet):
    serializer_class = serializers.ProductImageSerializer

    def get_queryset(self):
        return models.ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
