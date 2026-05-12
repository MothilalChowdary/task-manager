import pytest
from rest_framework import status
from django.urls import reverse
from users.models import User

@pytest.mark.django_db
class TestUserAPI:
    def test_user_registration_success(self, api_client):
        url = "/api/users/"
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == "newuser"
        assert response.data['role'] == "member" # Default role in serializer
        
        # Verify password is not in response
        assert 'password' not in response.data

    def test_registration_duplicate_email(self, api_client, create_user):
        create_user(email="taken@example.com")
        url = "/api/users/"
        data = {
            "username": "otheruser",
            "email": "taken@example.com",
            "password": "password123"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already exists" in str(response.data)

    def test_unauthenticated_profile_access(self, api_client):
        url = "/api/users/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
