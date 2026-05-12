import pytest
from rest_framework import status
from projects.models import Project
from datetime import date

@pytest.mark.django_db
class TestProjectAPI:
    def test_admin_can_create_project(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = "/api/projects/"
        data = {
            "title": "New Project",
            "description": "Description",
            "deadline": "2026-12-31",
            "members": []
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "New Project"
        assert Project.objects.filter(title="New Project").exists()

    def test_member_cannot_create_project(self, api_client, member_user):
        api_client.force_authenticate(user=member_user)
        url = "/api/projects/"
        data = {"title": "Fail", "description": "Fail", "deadline": "2026-12-31"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_projects_visibility(self, api_client, create_user):
        user1 = create_user(username="u1")
        user2 = create_user(username="u2")
        
        # Project 1: User 1 is creator
        p1 = Project.objects.create(title="P1", created_by=user1, deadline="2026-12-31")
        # Project 2: User 2 is creator, User 1 is member
        p2 = Project.objects.create(title="P2", created_by=user2, deadline="2026-12-31")
        p2.members.add(user1)
        # Project 3: User 2 is creator, User 1 is NOT member
        p3 = Project.objects.create(title="P3", created_by=user2, deadline="2026-12-31")

        api_client.force_authenticate(user=user1)
        response = api_client.get("/api/projects/")
        
        assert response.status_code == status.HTTP_200_OK
        titles = [p['title'] for p in response.data]
        assert "P1" in titles
        assert "P2" in titles
        assert "P3" not in titles

    def test_delete_project_only_by_creator(self, api_client, create_user):
        admin1 = create_user(username="admin1", role="admin")
        admin2 = create_user(username="admin2", role="admin")
        project = Project.objects.create(title="Creator P", created_by=admin1, deadline="2026-12-31")

        # Admin 2 tries to delete Admin 1's project
        api_client.force_authenticate(user=admin2)
        response = api_client.delete(f"/api/projects/{project.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_project_invalid_date(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = "/api/projects/"
        data = {"title": "Test", "description": "Desc", "deadline": "not-a-date"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "deadline" in response.data

    @pytest.mark.parametrize("invalid_title", ["", " "])
    def test_create_project_bad_titles(self, api_client, admin_user, invalid_title):
        api_client.force_authenticate(user=admin_user)
        url = "/api/projects/"
        data = {"title": invalid_title, "description": "Desc", "deadline": "2026-12-31"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
