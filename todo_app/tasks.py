from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Todo
import time

User = get_user_model()

@shared_task
def send_todos_email(user_id):
    time.sleep(20) # Simulate a delay for demonstration purposes
    user = User.objects.get(id=user_id)
    todos = Todo.objects.active().filter(user=user)

    if not todos.exists():
        body = "You have no active todos 🎉"
    else:
        body = "\n".join([f"- {t.title}" for t in todos])

    send_mail(
        subject="Your Todo List 📝",
        message=body,
        from_email="noreply@todoapp.com",
        recipient_list=[user.email],
    )
