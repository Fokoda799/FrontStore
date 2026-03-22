from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db.models import Count
from django.shortcuts import get_object_or_404

from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializers


@api_view(["GET", "POST"])
def products_list(request):
    if request.method == "GET":
        query_set = Product.objects.select_related("collection").all()[:5]
        serializer = ProductSerializers(
            query_set, many=True, context={"request": request}
        )
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProductSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "GET":
        serializer = ProductSerializers(product)
        return Response(serializer.data)
    elif request.method == "PATCH":
        serializer = ProductSerializers(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        if product.orderitems.count() > 0:
            return Response(
                {"error": "There is order items associated with this product"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def collection_list(request):
    if request.method == "GET":
        query_set = Collection.objects.annotate(products_count=Count("products")).all()[
            :5
        ]
        serializer = CollectionSerializer(query_set, many=True)
        return Response(serializer.data)
    if request.method == "POST":
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
def collection_details(request, pk):
    collection = get_object_or_404(
        Collection.objects.annotate(products_count=Count("products")), pk=pk
    )
    if request.method == "GET":
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    if request.method == "PATCH":
        serializer = CollectionSerializer(collection, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    if request.method == "DELETE":
        if collection.products.count() > 0:
            return Response(
                {"error": "There is products associated with this collection"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
