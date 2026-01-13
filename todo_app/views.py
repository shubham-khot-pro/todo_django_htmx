from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Todo, TodoEvent


# Create your views here.

def is_api(request):
    return request.headers.get("Accept") == "application/json"

# serializer - converts a Todo object to a dictionary
def todo_to_dict(todo):
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "created_at": todo.created_at,
        "updated_at": todo.updated_at,
    }

def index(request):
    todos = Todo.objects.order_by('-created_at')

    return render(request, 'todo_list.html', {'todos': todos})

def create_todo(request):
    if (request.method == "POST"):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        # simple duplicate check (case-insensitive)
        if Todo.objects.filter(title__iexact=title).exists():
            return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        todo = Todo.objects.create(title=title, description=description)
        TodoEvent.objects.create(todo=todo, event_type="created", details={'title': title})
        todos = Todo.objects.order_by('-created_at')

        if is_api(request):
            return JsonResponse(
                {"message": "Todo created", "todo": todo_to_dict(todo)},
                status=201
            )

        return render(request, 'partials/todo_list.html', {'todos': todos})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)

    todo.completed = not todo.completed
    todo.save()

    event_type = (
        TodoEvent.TODO_CHECKED
        if todo.completed
        else TodoEvent.TODO_UNCHECKED
    )

    TodoEvent.objects.create(
        todo=todo,
        event_type=event_type,
        details={'completed': todo.completed}
    )

    if is_api(request):
        return JsonResponse(
            {"message": "Todo status updated", "todo": todo_to_dict(todo)},
            status=200
        )

    return render(request, 'partials/todo_item.html', {'todo': todo})

def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'GET':
        return render(request, 'partials/todo_edit_form.html', {'todo': todo})
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    if not title:
        return JsonResponse({'error': 'Title required'}, status=400)
    if Todo.objects.exclude(pk=todo.pk).filter(title__iexact=title).exists():
        return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
    
    if todo.title.lower() == title.lower() and todo.description == description:
        return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        
    old = {'title': todo.title, 'description': todo.description}
    todo.title = title
    todo.description = description
    todo.save()
    TodoEvent.objects.create(todo=todo, event_type=TodoEvent.TODO_UPDATED, details={'old': old, 'new': {'title': title, 'description': description}})

    if is_api(request):
        return JsonResponse(
            {"message": "Todo updated", "todo": todo_to_dict(todo)},
            status=200
        )
   
    return render(request, 'partials/todo_item.html', {'todo': todo})


def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    TodoEvent.objects.create(todo=todo, event_type=TodoEvent.TODO_DELETED, details={'title': todo.title})
    todo.delete()
    todos = Todo.objects.order_by('-created_at')
    if is_api(request):
        return JsonResponse(
            {"message": "Todo deleted"},
            status=200
        )
    return render(request, 'partials/todo_list.html', {'todos': todos})


def todo_history(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    events = todo.events.all()

    if is_api(request):
        return JsonResponse(
            {
                "todo_id": todo.id,
                "history": [
                    {
                        "event": e.event_type,
                        "details": e.details,
                        "created_at": e.created_at,
                    }
                    for e in events
                ],
            },
            status=200,
        )
    
    return render(request, 'partials/todo_history.html', {'todo': todo, 'events': events})

