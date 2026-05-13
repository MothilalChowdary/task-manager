import pytest
from rest_framework import status
from projects.models import Project
from tasks.models import Task

@pytest.mark.django_db
class TestTaskAPI:
    @pytest.fixture
    def setup_data(self, create_user):
        admin = create_user(username="admin_test", role="admin")
        member = create_user(username="member_test", role="member")
        other_member = create_user(username="other_test", role="member")
        
        project = Project.objects.create(title="Project T", created_by=admin, deadline="2026-12-31")
        project.members.add(member)
        
        return admin, member, other_member, project

    def test_admin_can_create_task(self, api_client, setup_data):
        admin, member, _, project = setup_data
        api_client.force_authenticate(user=admin)
        url = "/api/tasks/"
        data = {
            "title": "Task 1",
            "description": "Desc",
            "project": project.id,
            "assigned_to": member.id,
            "deadline": "2026-12-31"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_member_cannot_create_task(self, api_client, setup_data):
        _, member, _, project = setup_data
        api_client.force_authenticate(user=member)
        url = "/api/tasks/"
        data = {"title": "No", "project": project.id, "assigned_to": member.id, "deadline": "2026-12-31"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_visibility_filtering(self, api_client, setup_data):
        admin, member, other_member, project = setup_data
        
        # Task in project user belongs to
        Task.objects.create(title="T1", project=project, assigned_to=member, deadline="2026-12-31")
        
        # Another project user DOES NOT belong to
        p2 = Project.objects.create(title="P2", created_by=admin, deadline="2026-12-31")
        Task.objects.create(title="T2", project=p2, assigned_to=other_member, deadline="2026-12-31")

        api_client.force_authenticate(user=member)
        response = api_client.get("/api/tasks/")
        
        assert response.status_code == status.HTTP_200_OK
        titles = [t['title'] for t in response.data]
        assert "T1" in titles
        assert "T2" not in titles

    def test_project_detail_serializer_logic(self, api_client, setup_data):
        """Tests ProjectSerializer.get_tasks logic"""
        admin, member, other_member, project = setup_data
        
        # Task assigned to current member
        Task.objects.create(title="My Task", project=project, assigned_to=member, deadline="2026-12-31")
        # Task assigned to someone else in same project
        Task.objects.create(title="Other Task", project=project, assigned_to=other_member, deadline="2026-12-31")

        api_client.force_authenticate(user=member)
        response = api_client.get(f"/api/projects/{project.id}/")
        
        tasks_in_project = response.data['tasks']
        assert len(tasks_in_project) == 1
        assert tasks_in_project[0]['title'] == "My Task"

    def test_member_can_complete_task(self, api_client, setup_data):
        admin, member, _, project = setup_data
        task = Task.objects.create(
            title="Work", project=project, assigned_to=member, 
            status="pending", deadline="2026-12-31"
        )
        
        api_client.force_authenticate(user=member)
        url = f"/api/tasks/{task.id}/"
        response = api_client.patch(url, {"status": "completed"})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == "completed"

    def test_cannot_assign_non_member_to_task(self, api_client, setup_data):
        admin, _, other_member, project = setup_data
        api_client.force_authenticate(user=admin)
        url = "/api/tasks/"
        data = {
            "title": "Invalid Task",
            "project": project.id,
            "assigned_to": other_member.id, # other_member is NOT in project.members
            "deadline": "2026-12-31"
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "member of the project" in str(response.data).lower()

    def test_member_cannot_change_task_title(self, api_client, setup_data):
        _, member, _, project = setup_data
        task = Task.objects.create(title="Original Title", project=project, assigned_to=member, deadline="2026-12-31")
        
        api_client.force_authenticate(user=member)
        url = f"/api/tasks/{task.id}/"
        # Member tries to change status (allowed) AND title (should be ignored/read-only)
        response = api_client.patch(url, {"status": "completed", "title": "Hacked Title"})
        
        task.refresh_from_db()
        assert task.status == "completed"
        assert task.title == "Original Title" # Should NOT have changed
