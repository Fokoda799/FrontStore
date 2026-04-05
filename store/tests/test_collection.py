import pytest
from model_bakery import baker
from rest_framework import status

from store.models import Collection


def collection_detail_url(id):
    return f"/store/collections/{id}/"


@pytest.mark.django_db
class TestCreateCollection:

    endpoint = "/store/collections/"

    def test_anonymous_returns_401(self, api_client):
        """_summary_

        Args:
            api_client (APIClient): _description_
        """

        response = api_client.post(
            self.endpoint,
            {"title": "Test Collection"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_user_not_admin_returns_403(
        self,
        api_client,
        auth_user,
        authenticate,
    ):
        authenticate(auth_user)

        response = api_client.post(
            self.endpoint,
            {"title": "Test Collection"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_invalid_data_returns_400(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        authenticate(admin_user)

        # Invalid → missing required field
        response = api_client.post(
            self.endpoint,
            {},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_valid_data_returns_201(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        authenticate(admin_user)

        response = api_client.post(
            self.endpoint,
            {"title": "Valid Collection"},
        )

        assert Collection.objects.filter(title="Valid Collection").exists()

        assert response.status_code == status.HTTP_201_CREATED

        assert response.data["id"] > 0
        assert response.data["title"] == "Valid Collection"


@pytest.mark.django_db
class TestRetrieveCollection:

    def test_collection_not_exist_return_404(self, api_client):

        response = api_client.get(collection_detail_url(1))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_collection_exists_return_200(self, api_client):

        collection = baker.make(Collection)

        response = api_client.get(collection_detail_url(collection.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0,
            "featured_product": None,
        }


@pytest.mark.django_db
class TestListCollections:

    endpoint = "/store/collections/"

    def test_list_all_collections_return_200(self, api_client):

        response = api_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5


@pytest.mark.django_db
class TestUpdateCollection:

    def test_anonymous_returns_401(self, api_client):
        collection = baker.make(Collection)

        response = api_client.put(
            collection_detail_url(collection.id),
            {"title": "Updated"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_user_not_admin_returns_403(
        self,
        api_client,
        auth_user,
        authenticate,
    ):
        collection = baker.make(Collection)

        authenticate(auth_user)

        response = api_client.put(
            collection_detail_url(collection.id),
            {"title": "Updated"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_invalid_data_returns_400(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        collection = baker.make(Collection)

        authenticate(admin_user)

        response = api_client.put(
            self.endpoint(collection.id),
            {},  # invalid payload
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_valid_data_returns_200(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        collection = baker.make(Collection)

        authenticate(admin_user)

        response = api_client.put(
            collection_detail_url(collection.id),
            {"title": "Updated Collection"},
        )

        assert response.status_code == status.HTTP_200_OK

        collection.refresh_from_db()

        assert collection.title == "Updated Collection"


@pytest.mark.django_db
class TestDeleteCollection:

    endpoint = lambda self, id: f"/store/collections/{id}/"  # noqa: E731

    def test_anonymous_returns_401(self, api_client):
        collection = baker.make(Collection)

        response = api_client.delete(self.endpoint(collection.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_user_not_admin_returns_403(
        self,
        api_client,
        auth_user,
        authenticate,
    ):
        collection = baker.make(Collection)

        authenticate(auth_user)

        response = api_client.delete(collection_detail_url(collection.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_returns_204(
        self,
        api_client,
        admin_user,
        authenticate,
    ):
        collection = baker.make(Collection)

        authenticate(admin_user)

        response = api_client.delete(collection_detail_url(collection.id))

        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert Collection.objects.filter(id=collection.id).count() == 0
