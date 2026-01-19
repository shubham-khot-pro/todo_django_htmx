# todo_app/context_processors.py
from .models import Todo

def todo_manager(request):
    return {
        'todo_manager': {
            'deleted': {
                'count': Todo.objects.deleted().count()
            }
        }
    }