"""Lightweight Task model (optional persistence) used only if you wish to store tasks.
For the assignment, the API primarily accepts tasks via JSON POST requests and processes them in-memory.
"""
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.IntegerField(default=1)
    importance = models.IntegerField(default=5)
    dependencies = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title
