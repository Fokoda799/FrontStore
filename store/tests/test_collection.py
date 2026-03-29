import pytest
from model_bakery import baker
from rest_framework import status

from store.models import Collection


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

        assert response.status_code == status.HTTP_201_CREATED

        assert response.data["id"] > 0
        assert response.data["title"] == "Valid Collection"


@pytest.mark.django_db
class TestRetrieveCollection:

    endpoint = lambda self, id: f"/store/collections/{id}/"  # noqa: E731

    def test_collection_not_exist_return_404(self, api_client):

        response = api_client.get(self.endpoint(1))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_collection_exists_return_200(self, api_client):

        collection = baker.make(Collection)

        response = api_client.get(self.endpoint(collection.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0,
            "featured_product": None,
        }
