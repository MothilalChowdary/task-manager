from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id','created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.role == 'member':
            for field_name in self.fields:
                if field_name != 'status':
                    self.fields[field_name].read_only = True

    def validate(self, data):
        request = self.context.get('request')
        if not request: return data
        
        if request.user.role == 'admin':
            project = data.get('project') or (self.instance.project if self.instance else None)
            assigned_to = data.get('assigned_to') or (self.instance.assigned_to if self.instance else None)
            
            if project and assigned_to:
                if assigned_to not in project.members.all():
                    raise serializers.ValidationError("Assigned user must be a member of the project.")
        return data