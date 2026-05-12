from rest_framework import serializers
from .models import Project
from tasks.serializers import TaskSerializer

class ProjectSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'created_by', 'members', 'status', 'deadline', 'created_at', 'tasks']
        read_only_fields = ['id','created_by', 'created_at']

    def get_tasks(self, obj):
        user = self.context['request'].user

        if user.role == 'admin':
            return TaskSerializer(obj.tasks.all(), many=True,context=self.context).data

        return TaskSerializer(obj.tasks.filter(assigned_to=user),many=True,context=self.context).data