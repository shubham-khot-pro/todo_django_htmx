# todo_app/signals.py
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Todo, TodoEvent

@receiver(pre_save, sender=Todo)
def track_state_changes(sender, instance, **kwargs):
    """
    Before saving, capture the old state of the object so we can compare later.
    """
    if instance.pk:
        try:
            old_instance = Todo.objects.get(pk=instance.pk)
            instance._old_completed = old_instance.completed
            instance._old_is_deleted = old_instance.is_deleted
            instance._old_title = old_instance.title
            instance._old_desc = old_instance.description
        except Todo.DoesNotExist:
            pass
    else:
        # It's a new object
        instance._old_completed = None
        instance._old_is_deleted = False

@receiver(post_save, sender=Todo)
def log_todo_save(sender, instance, created, **kwargs):
    """
    After saving, check what changed and create the appropriate event.
    """
    # 1. Try to get the user who triggered this (see Step C)
    # If no user was attached (e.g., admin panel or shell), fall back to the Todo owner or None
    user = getattr(instance, '_current_user', instance.user)

    event_type = None
    details = {}

    if created:
        event_type = TodoEvent.TODO_CREATED
        details = {'title': instance.title}
    else:
        # Detect Soft Delete
        if instance.is_deleted and not getattr(instance, '_old_is_deleted', False):
            event_type = TodoEvent.TODO_DELETED
            details = {'title': instance.title}
        
        # Detect Restore
        elif not instance.is_deleted and getattr(instance, '_old_is_deleted', False):
            event_type = TodoEvent.TODO_RESTORED
            details = {'title': instance.title}
        
        # Detect Completed/Uncompleted
        elif instance.completed != getattr(instance, '_old_completed', None):
            event_type = TodoEvent.TODO_CHECKED if instance.completed else TodoEvent.TODO_UNCHECKED
            details = {'completed': instance.completed, 'title': instance.title}
        
        # Detect General Update (Title/Description)
        elif (instance.title != getattr(instance, '_old_title', '') or 
              instance.description != getattr(instance, '_old_desc', '')):
            event_type = TodoEvent.TODO_UPDATED
            details = {
                'old': {'title': getattr(instance, '_old_title', ''), 'description': getattr(instance, '_old_desc', '')},
                'new': {'title': instance.title, 'description': instance.description}
            }

    # Only create event if we identified a type
    if event_type:
        TodoEvent.objects.create(
            user=user,
            todo=instance,
            event_type=event_type,
            details=details
        )

# @receiver(post_delete, sender=Todo)
# def log_todo_hard_delete(sender, instance, **kwargs):
#     """
#     Logs when a record is permanently removed from the DB.
#     """
#     user = getattr(instance, '_current_user', instance.user)
    
#     # Note: We must create the event BEFORE the cascade delete might wipe it, 
#     # but post_delete usually happens after. 
#     # Ideally, for hard deletes, you log manually in the view OR set on_delete=SET_NULL for events.
#     # Assuming you want to try capturing it:
    
#     # Warning: If TodoEvent has on_delete=CASCADE pointing to Todo, 
#     # this event will be deleted immediately too! 
#     # You might want to remove this specific signal if you want to keep history of dead items,
#     # or ensure your TodoEvent.todo field is nullable / set_null.
#     pass