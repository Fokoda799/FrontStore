from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from django.db.models import Count

from . import models, serializers
from .filters import ProductFilter


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.annotate(
        products_count=Count("products")
    ).all()
    serializer_class = serializers.CollectionSerializer

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
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination
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
    queryset = models.Cart.objects.prefetch_related("items__product").all()
    serializer_class = serializers.CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_name = ["get", "post", "patch", "delete"]

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
