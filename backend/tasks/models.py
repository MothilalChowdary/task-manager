from django.db import models
from users.models import User
from projects.models import Project
# Create your models here.

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending','Pending'),
        ('in_progress','In Progress'),
        ('completed','Completed')
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)