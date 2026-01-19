# models.py
"""
Models for Todo application with abstract base models and soft delete functionality.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import TodoManager


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is Deleted"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Deleted At"))
    
    def soft_delete(self):
        """Mark the instance as deleted without removing it from database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def restore(self):
        """Restore a soft-deleted instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    class Meta:
        abstract = True


class Todo(TimeStampedModel, SoftDeleteModel):
    """
    Todo item model with soft delete functionality.
    """
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    completed = models.BooleanField(default=False, verbose_name=_("Completed"))
    
    # Custom manager
    objects = TodoManager()
    
    def __str__(self):
        return f"{self.title} ({'Completed' if self.completed else 'Pending'})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Todo")
        verbose_name_plural = _("Todos")
        # Example of managed=False (for reference - not enabled here)
        # managed = False  # Django won't create or delete table for this model


class TodoEvent(TimeStampedModel):
    """
    Event log for tracking todo item changes.
    """
    TODO_CREATED = 'created'
    TODO_UPDATED = 'updated'
    TODO_CHECKED = 'checked'
    TODO_UNCHECKED = 'unchecked'
    TODO_DELETED = 'deleted'
    TODO_RESTORED = 'restored'
    TODO_PERMANENTLY_DELETED = 'permanently_deleted'
    
    EVENT_CHOICES = [
        (TODO_CREATED, 'Created'),
        (TODO_UPDATED, 'Updated'),
        (TODO_CHECKED, 'Checked'),
        (TODO_UNCHECKED, 'Unchecked'),
        (TODO_DELETED, 'Soft Deleted'),
        (TODO_RESTORED, 'Restored'),
        (TODO_PERMANENTLY_DELETED, 'Permanently Deleted'),
    ]
    
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES, verbose_name=_("Event Type"))
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Timestamp"))
    details = models.JSONField(blank=True, null=True, verbose_name=_("Details"))
    
    def __str__(self):
        return f"{self.todo.title} - {self.get_event_type_display()} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Todo Event")
        verbose_name_plural = _("Todo Events")
        # Example of managed=False (for reference)
        # managed = False  # Useful when table already exists in DB

# from django.db import models
# from django.utils import timezone


# class Todo(models.Model):
# 	title = models.CharField(max_length=200)
# 	description = models.TextField(blank=True)
# 	completed = models.BooleanField(default=False)
# 	created_at = models.DateTimeField(auto_now_add=True)
# 	updated_at = models.DateTimeField(auto_now=True)

	

# class TodoEvent(models.Model):
# 	TODO_CREATED = 'created'
# 	TODO_UPDATED = 'updated'
# 	TODO_CHECKED = 'checked'
# 	TODO_UNCHECKED = 'unchecked'
# 	TODO_DELETED = 'deleted'

# 	EVENT_CHOICES = [
# 		(TODO_CREATED, 'Created'),
# 		(TODO_UPDATED, 'Updated'),
# 		(TODO_CHECKED, 'Checked'),
# 		(TODO_UNCHECKED, 'Unchecked'),
# 		(TODO_DELETED, 'Deleted'),
# 	]

# 	todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='events')
# 	event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
# 	timestamp = models.DateTimeField(default=timezone.now)
# 	details = models.JSONField(blank=True, null=True)

# 	class Meta:
# 		ordering = ['-timestamp']

	