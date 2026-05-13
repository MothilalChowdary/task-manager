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
        assert response.data['role'] == "member" 
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
        assert "exists" in str(response.data).lower()

    def test_unauthenticated_profile_access(self, api_client):
        url = "/api/users/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self, api_client, create_user):
        user = create_user(username="testuser", password="old_password_123")
        api_client.force_authenticate(user=user)
        url = "/api/users/change-password/"
        data = {
            "old_password": "old_password_123",
            "new_password": "new_password_456",
            "confirm_password": "new_password_456"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password changed
        user.refresh_from_db()
        assert user.check_password("new_password_456")

    def test_change_password_wrong_old(self, api_client, create_user):
        user = create_user(username="testuser", password="correct_password")
        api_client.force_authenticate(user=user)
        url = "/api/users/change-password/"
        data = {
            "old_password": "wrong_password",
            "new_password": "new_password",
            "confirm_password": "new_password"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_mismatch(self, api_client, create_user):
        user = create_user(password="correct_password")
        api_client.force_authenticate(user=user)
        url = "/api/users/change-password/"
        data = {
            "old_password": "correct_password",
            "new_password": "new_password_1",
            "confirm_password": "new_password_2"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirm_password" in response.data

    def test_jwt_refresh_flow(self, api_client, create_user):
        user = create_user(username="refresh_user", password="password123")
        # 1. Get initial tokens
        login_res = api_client.post("/api/token/", {"username": "refresh_user", "password": "password123"})
        refresh_token = login_res.data['refresh']
        
        # 2. Use refresh token to get a new access token
        refresh_res = api_client.post("/api/token/refresh/", {"refresh": refresh_token})
        assert refresh_res.status_code == status.HTTP_200_OK
        assert "access" in refresh_res.data

    def test_member_cannot_promote_self(self, api_client, create_user):
        member = create_user(username="hacker", role="member")
        api_client.force_authenticate(user=member)
        url = f"/api/users/{member.id}/"
        
        # Try to change role to admin
        response = api_client.patch(url, {"role": "admin"})
        
        member.refresh_from_db()
        assert member.role == "member" # Role remains member because it's read-only
