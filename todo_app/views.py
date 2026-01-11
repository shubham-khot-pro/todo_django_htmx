from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from .models import Todo, TodoEvent


# Create your views here.

def index(request):
    todos = Todo.objects.order_by('-created_at')

    return render(request, 'todo_list.html', {'todos': todos})

def create_todo(request):
    if (request.method == "POST"):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        if not title:
            return HttpResponseBadRequest('Title is required')
        # simple duplicate check (case-insensitive)
        if Todo.objects.filter(title__iexact=title).exists():
            return HttpResponseBadRequest('A todo with this title already exists')
        todo = Todo.objects.create(title=title, description=description)
        TodoEvent.objects.create(todo=todo, event_type="created", details={'title': title})
        todos = Todo.objects.order_by('-created_at')
        return render(request, 'partials/todo_list.html', {'todos': todos})

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

    return render(request, 'partials/todo_item.html', {'todo': todo})

def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'GET':
        return render(request, 'partials/todo_edit_form.html', {'todo': todo})
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    if not title:
        return HttpResponseBadRequest('Title required')
    if Todo.objects.exclude(pk=todo.pk).filter(title__iexact=title).exists():
        return HttpResponseBadRequest('A todo with this title already exists')
    
    if todo.title.lower() == title.lower() and todo.description == description:
            return HttpResponseBadRequest('A todo with this title already exists')
        
    old = {'title': todo.title, 'description': todo.description}
    todo.title = title
    todo.description = description
    todo.save()
    TodoEvent.objects.create(todo=todo, event_type=TodoEvent.TODO_UPDATED, details={'old': old, 'new': {'title': title, 'description': description}})
   
    return render(request, 'partials/todo_item.html', {'todo': todo})


def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    TodoEvent.objects.create(todo=todo, event_type=TodoEvent.TODO_DELETED, details={'title': todo.title})
    todo.delete()
    todos = Todo.objects.order_by('-created_at')
    return render(request, 'partials/todo_list.html', {'todos': todos})


def todo_history(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    events = todo.events.all()
    return render(request, 'partials/todo_history.html', {'todo': todo, 'events': events})

