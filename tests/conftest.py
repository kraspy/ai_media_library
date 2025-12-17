import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def api_client() -> Client:
    """Fixture to provide a Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(api_client: Client) -> Client:
    """Fixture to provide an authenticated Django test client."""
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    api_client.force_login(user)
    return api_client


@pytest.fixture
def admin_client(api_client: Client) -> Client:
    """Fixture to provide an admin authenticated Django test client."""
    admin_user = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )
    api_client.force_login(admin_user)
    return api_client


@pytest.fixture
def create_user():
    """Fixture factory to create test users."""

    def _create_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass
