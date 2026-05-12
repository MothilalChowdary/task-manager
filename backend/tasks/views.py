from django.shortcuts import render
from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer
from users.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class TaskViewset(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')
        if user.role == 'admin':
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(project__members=user)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset