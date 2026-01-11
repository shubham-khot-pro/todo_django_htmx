from django.db import models
from django.utils import timezone


class Todo(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	completed = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	

class TodoEvent(models.Model):
	TODO_CREATED = 'created'
	TODO_UPDATED = 'updated'
	TODO_CHECKED = 'checked'
	TODO_UNCHECKED = 'unchecked'
	TODO_DELETED = 'deleted'

	EVENT_CHOICES = [
		(TODO_CREATED, 'Created'),
		(TODO_UPDATED, 'Updated'),
		(TODO_CHECKED, 'Checked'),
		(TODO_UNCHECKED, 'Unchecked'),
		(TODO_DELETED, 'Deleted'),
	]

	todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='events')
	event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
	timestamp = models.DateTimeField(default=timezone.now)
	details = models.JSONField(blank=True, null=True)

	class Meta:
		ordering = ['-timestamp']

	