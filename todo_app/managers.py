# todo_app/managers.py
"""
Custom QuerySet managers for Todo application.
"""

from django.db import models
from django.utils import timezone


class TodoQuerySet(models.QuerySet):
    """Custom QuerySet for Todo model."""
    
    def active(self):
        """Return only non-deleted todos."""
        return self.filter(is_deleted=False)
    
    def deleted(self):
        """Return only soft-deleted todos."""
        return self.filter(is_deleted=True)
    
    def completed(self):
        """Return only completed todos."""
        return self.filter(completed=True)
    
    def pending(self):
        """Return only pending todos."""
        return self.filter(completed=False)
    
    def created_today(self):
        """Return todos created today."""
        today = timezone.now().date()
        return self.filter(created_at__date=today)
    
    def with_recent_events(self, days=7):
        """Return todos with events in last N days."""
        from .models import TodoEvent
        recent_date = timezone.now() - timezone.timedelta(days=days)
        event_ids = TodoEvent.objects.filter(
            timestamp__gte=recent_date
        ).values_list('todo_id', flat=True)
        return self.filter(id__in=event_ids)


class TodoManager(models.Manager):
    """Custom manager for Todo model."""
    
    def get_queryset(self):
        return TodoQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def deleted(self):
        return self.get_queryset().deleted()
    
    def completed(self):
        return self.get_queryset().completed()
    
    def pending(self):
        return self.get_queryset().pending()