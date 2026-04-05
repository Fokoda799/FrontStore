import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        return User.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def admin_user(create_user):
    return create_user(
        username="admin",
        email="admin@test.com",
        password="123456",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def auth_user(create_user):
    return create_user(
        username="user",
        email="user@test.com",
        password="123456",
        is_staff=False,
    )


@pytest.fixture
def authenticate(api_client):
    def do_auth(user):
        api_client.force_authenticate(user=user)

    return do_auth


@pytest.fixture
def image_file():
    return SimpleUploadedFile(
        name="test.jpg",
        content=b"file_content",
        content_type="image/jpeg",
    )
