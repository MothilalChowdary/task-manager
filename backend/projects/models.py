from django.db import models
from users.models import User
# Create your models here.
class Project(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    members = models.ManyToManyField(User,related_name='projects')
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='active')
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    