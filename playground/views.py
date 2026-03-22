from django.shortcuts import render


def say_hello(request):
    # productFirst = Product.objects.filter(pk=1).first()
    # productExists = Product.objects.filter(pk=2).exists()
    # productsFilter = Product.objects.filter(price__range=(20, 30))
    # productLatest = Product.objects.latest('-price')
    # productEarliest = Product.objects.earliest('price')
    # productLimit = list(Product.objects.all()[:5])
    # productLimitPage = list(Product.objects.all()[5:10])

    # query_set = Product.objects.filter(~Q(
    #     id__in=OrderItem.objects.values('product_id').distinct()
    # )).order_by('title').defer('price')

    # query_set = Product.objects.select_related('collection').all()
    # query_set = Product.objects.prefetch_related('promotions').all()

    # query_set = Order.objects.select_related(
    #     'costumer').prefetch_related('orderitem_set__product').order_by(
    #         '-placed_at')[:5]

    # discounted_price = ExpressionWrapper(F('price') * 0.8,
    # output_field=DecimalField())

    # query_set = Product.objects.annotate(
    #     discounted_price=discounted_price
    # )

    # tags = list(TaggedItem.objects.get_tags_for(Product, 1))

    # with transaction.atomic():
    #     order = Order.objects.create(costumer_id=1)

    #     item = OrderItem.objects.create(
    #         order=order,
    #         product_id=-1,
    #         quantity=4,
    #         unite_price=10
    #     )

    return render(request, "index.html")
