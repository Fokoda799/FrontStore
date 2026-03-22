from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.db.models import Count

from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializers


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers

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


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        collection = self.get_object()
        if Collection.products.count() > 0:
            return Response(
                {"error": "There are products associated with this collection"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(collection)
        return Response(status=status.HTTP_204_NO_CONTENT)
