import pytest
from model_bakery import baker
from rest_framework import status

from store.models import Collection, Product, ProductImage, Review

# =========================================================
# CREATE PRODUCT
# =========================================================


@pytest.mark.django_db
class TestCreateProduct:

    endpoint = "/store/products/"

    def test_anonymous_returns_401(self, api_client):
        collection = baker.make(Collection)

        response = api_client.post(
            self.endpoint,
            {
                "title": "Test Product",
                "unit_price": 10,
                "collection": collection.id,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_non_admin_returns_403(
        self,
        api_client,
        auth_user,
        authenticate,
    ):

        collection = baker.make(Collection)

        authenticate(auth_user)

        response = api_client.post(
            self.endpoint,
            {
                "title": "Test Product",
                "unit_price": 10,
                "collection": collection.id,
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_valid_returns_201(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        collection = baker.make(Collection)

        authenticate(admin_user)

        response = api_client.post(
            self.endpoint,
            {
                "title": "Valid Product",
                "unit_price": 20,
                "collection": collection.id,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        assert Product.objects.filter(title="Valid Product").exists()


# =========================================================
# RETRIEVE PRODUCT
# =========================================================


@pytest.mark.django_db
class TestRetrieveProduct:

    def test_product_not_found_returns_404(
        self,
        api_client,
    ):
        response = api_client.get(self.endpoint(1))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_product_exists_returns_200(
        self,
        api_client,
    ):
        product = baker.make(Product)

        response = api_client.get(self.endpoint(product.id))

        assert response.status_code == status.HTTP_200_OK

        assert response.data["id"] == product.id


# =========================================================
# LIST PRODUCTS
# =========================================================


@pytest.mark.django_db
class TestListProducts:

    endpoint = "/store/products/"

    def test_list_products_returns_200(
        self,
        api_client,
    ):
        baker.make(Product, _quantity=5)

        response = api_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5


# =========================================================
# ORDERING
# =========================================================


@pytest.mark.django_db
class TestProductOrdering:

    endpoint = "/store/products/"

    def test_order_by_price(
        self,
        api_client,
    ):
        baker.make(Product, unit_price=10)
        baker.make(Product, unit_price=30)
        baker.make(Product, unit_price=20)

        response = api_client.get(self.endpoint + "?ordering=unit_price")

        prices = [item["unit_price"] for item in response.data]

        assert prices == sorted(prices)


# =========================================================
# FILTERING
# =========================================================


@pytest.mark.django_db
class TestProductFiltering:

    endpoint = "/store/products/"

    def test_filter_by_collection(
        self,
        api_client,
    ):
        c1 = baker.make(Collection)
        c2 = baker.make(Collection)

        p1 = baker.make(Product, collection=c1)
        baker.make(Product, collection=c2)

        response = api_client.get(f"{self.endpoint}?collection_id={c1.id}")

        ids = [p["id"] for p in response.data]

        assert p1.id in ids
        assert len(ids) == 1

    def test_filter_by_price_range(
        self,
        api_client,
    ):
        baker.make(Product, unit_price=10)
        baker.make(Product, unit_price=50)

        response = api_client.get(
            self.endpoint + "?unit_price__gt=20&unit_price__lt=100"
        )

        assert len(response.data) == 1


# =========================================================
# SEARCH
# =========================================================


@pytest.mark.django_db
class TestProductSearch:

    endpoint = "/store/products/"

    def test_search_by_title(
        self,
        api_client,
    ):
        p1 = baker.make(Product, title="Perfume")

        baker.make(Product, title="Laptop")

        response = api_client.get(self.endpoint + "?search=perf")

        ids = [p["id"] for p in response.data]

        assert p1.id in ids
        assert len(ids) == 1


# =========================================================
# REVIEWS
# =========================================================


@pytest.mark.django_db
class TestProductReviews:

    def test_list_reviews_returns_200(
        self,
        api_client,
    ):
        product = baker.make(Product)

        baker.make(
            Review,
            product=product,
            _quantity=3,
        )

        response = api_client.get(self.endpoint(product.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_review_authenticated_returns_201(
        self,
        api_client,
        auth_user,
        authenticate,
    ):
        product = baker.make(Product)

        authenticate(auth_user)

        response = api_client.post(
            self.endpoint(product.id),
            {
                "name": "User",
                "description": "Great product",
                "rating": 5,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        assert Review.objects.filter(product=product).exists()

    def test_delete_review_admin_returns_204(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        review = baker.make(Review)

        authenticate(admin_user)

        url = f"/store/products/" f"{review.product.id}/reviews/{review.id}/"

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert not Review.objects.filter(id=review.id).exists()


# =========================================================
# IMAGES
# =========================================================


@pytest.mark.django_db
class TestProductImages:

    def test_list_images_returns_200(
        self,
        api_client,
    ):
        product = baker.make(Product)

        baker.make(
            ProductImage,
            product=product,
            _quantity=2,
        )

        response = api_client.get(self.endpoint(product.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_upload_image_admin_returns_201(
        self,
        api_client,
        admin_user,
        authenticate,
        image_file,
    ):
        product = baker.make(Product)

        authenticate(admin_user)

        response = api_client.post(
            self.endpoint(product.id),
            {"image": image_file},
            format="multipart",
        )

        assert response.status_code == status.HTTP_201_CREATED
