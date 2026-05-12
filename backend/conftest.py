import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        if 'username' not in kwargs:
            kwargs['username'] = f"user_{User.objects.count()}"
        if 'email' not in kwargs:
            kwargs['email'] = f"{kwargs['username']}@example.com"
        password = kwargs.pop('password', 'password123')
        user = User.objects.create_user(**kwargs)
        user.set_password(password)
        user.save()
        return user
    return make_user

@pytest.fixture
def admin_user(create_user):
    return create_user(role='admin', username='admin_user')

@pytest.fixture
def member_user(create_user):
    return create_user(role='member', username='member_user')
