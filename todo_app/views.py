# views.py - COMPLETELY REPLACE WITH THIS
"""
Class-based views for Todo application with pagination and delete functionality.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Todo, TodoEvent


class TodoListView(TemplateView):
    """
    Display paginated list of active todo items with infinite scroll.
    """
    template_name = 'todo_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        per_page = 5
        
        todos = Todo.objects.active().order_by('-created_at')
        paginator = Paginator(todos, per_page)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        context.update({
            'todos': page_obj,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page,
        })
        return context


class CreateTodoView(View):
    """
    Handle creation of new todo items.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        if Todo.objects.active().filter(title__iexact=title).exists():
            return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        
        todo = Todo.objects.create(title=title, description=description)
        TodoEvent.objects.create(
            todo=todo,
            event_type=TodoEvent.TODO_CREATED,
            details={'title': title}
        )
        
        if request.htmx:
            # Return the new todo item
            return render(request, 'partials/todo_item.html', {'todo': todo})
        return redirect('todo_app:index')


class ToggleTodoView(View):
    """
    Toggle completion status of a todo item.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo.objects.active(), pk=pk)
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
            details={'completed': todo.completed, 'title': todo.title}
        )
        
        return render(request, 'partials/todo_item.html', {'todo': todo})


class EditTodoView(View):
    """
    Handle editing of todo items.
    """
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo.objects.active(), pk=pk)
        return render(request, 'partials/todo_edit_form.html', {'todo': todo})
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo.objects.active(), pk=pk)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            return JsonResponse({'error': 'Title required'}, status=400)
        
        if Todo.objects.active().exclude(pk=todo.pk).filter(title__iexact=title).exists():
            return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        
        if todo.title.lower() == title.lower() and todo.description == description:
            return JsonResponse({'error': 'No changes detected'}, status=400)
        
        old_data = {'title': todo.title, 'description': todo.description}
        todo.title = title
        todo.description = description
        todo.save()
        
        TodoEvent.objects.create(
            todo=todo,
            event_type=TodoEvent.TODO_UPDATED,
            details={
                'old': old_data,
                'new': {'title': title, 'description': description}
            }
        )
        
        return render(request, 'partials/todo_item.html', {'todo': todo})


class SoftDeleteTodoView(View):
    """
    Soft delete a todo item.
    """
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo.objects.active(), pk=pk)
        
        todo.soft_delete()
        
        TodoEvent.objects.create(
            todo=todo,
            event_type=TodoEvent.TODO_DELETED,
            details={'title': todo.title}
        )
        
        if request.htmx:
            # Return empty div to remove the todo from DOM
            return render(request, 'partials/empty.html')
        return redirect('todo_app:index')


class DeletedTodosView(TemplateView):
    """
    Display list of soft-deleted todo items with pagination.
    """
    template_name = 'deleted_todos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        per_page = 5
        
        todos = Todo.objects.deleted().order_by('-deleted_at')
        paginator = Paginator(todos, per_page)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        context.update({
            'todos': page_obj,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page,
        })
        return context


class RestoreTodoView(View):
    """
    Restore a soft-deleted todo item.
    """
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo.objects.deleted(), pk=pk)
        
        todo.restore()
        
        TodoEvent.objects.create(
            todo=todo,
            event_type=TodoEvent.TODO_RESTORED,
            details={'title': todo.title}
        )
        
        if request.htmx:
            # Return empty to remove from deleted list
            return render(request, 'partials/empty.html')
        return redirect('todo_app:deleted_todos')


class HardDeleteTodoView(View):
    """
    Permanently delete a todo item and all associated events.
    """
    
    def post(self, request, pk):
        todo = get_object_or_404(Todo.objects.deleted(), pk=pk)
        
        # Log event before deletion
        TodoEvent.objects.create(
            todo=todo,
            event_type=TodoEvent.TODO_PERMANENTLY_DELETED,
            details={'title': todo.title}
        )
        
        todo.delete()  # This cascades to delete related events
        
        if request.htmx:
            return render(request, 'partials/empty.html')
        return redirect('todo_app:deleted_todos')


class TodoHistoryView(View):
    """
    Display paginated history of events for a todo item.
    """
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo.objects.active(), pk=pk)
        page = int(request.GET.get('page', 1))
        per_page = 3
        
        events = todo.events.all().order_by('-timestamp')
        paginator = Paginator(events, per_page)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        return render(request, 'partials/todo_history.html', {
            'todo': todo,
            'events': page_obj,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        })

# In views.py, update LoadMoreTodosView:
class LoadMoreTodosView(View):
    """
    Load more todos with simple button.
    """
    
    def get(self, request):
        page = int(request.GET.get('page', 2))
        per_page = 5
        
        todos = Todo.objects.active().order_by('-created_at')
        paginator = Paginator(todos, per_page)
        
        try:
            page_obj = paginator.page(page)
        except:
            return render(request, 'partials/empty.html')
        
        context = {
            'todos': page_obj,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        }
        return render(request, 'partials/load_more_todos.html', context)

class LoadMoreDeletedTodosView(View):
    """
    Load more deleted todos with simple button.
    """
    
    def get(self, request):
        page = int(request.GET.get('page', 2))
        per_page = 5
        
        todos = Todo.objects.deleted().order_by('-deleted_at')
        paginator = Paginator(todos, per_page)
        
        try:
            page_obj = paginator.page(page)
        except:
            return render(request, 'partials/empty.html')
        
        context = {
            'todos': page_obj,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        }
        return render(request, 'partials/deleted_todo_items.html', context)

class LoadMoreHistoryView(View):
    """
    Load more history events with simple button.
    """
    
    def get(self, request, pk):
        todo = get_object_or_404(Todo.objects.active(), pk=pk)
        page = int(request.GET.get('page', 2))
        per_page = 3
        
        events = todo.events.all().order_by('-timestamp')
        paginator = Paginator(events, per_page)
        
        try:
            page_obj = paginator.page(page)
        except:
            return render(request, 'partials/empty.html')
        
        context = {
            'todo': todo,
            'events': page_obj,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        }
        return render(request, 'partials/history_items.html', context)
    


# from django.http import HttpResponseBadRequest, JsonResponse
# from django.shortcuts import get_object_or_404, render
# from .models import Todo, TodoEvent

# def index(request):
#     todos = Todo.objects.order_by('-created_at')

#     return render(request, 'todo_list.html', {'todos': todos})

# def create_todo(request):
#     if (request.method == "POST"):
#         title = request.POST.get('title', '').strip()
#         description = request.POST.get('description', '').strip()
#         if not title:
#             return JsonResponse({'error': 'Title is required'}, status=400)
#         # simple duplicate check (case-insensitive)
#         if Todo.objects.filter(title__iexact=title).exists():
#             return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
#         todo = Todo.objects.create(title=title, description=description)
#         TodoEvent.objects.create(todo=todo, event_type="created", details={'title': title})
#         todos = Todo.objects.order_by('-created_at')


#         return render(request, 'partials/todo_list.html', {'todos': todos})
#     else:
#         return JsonResponse({"error": "Method not allowed"}, status=405)

# def toggle_todo(request, pk):
#     todo = get_object_or_404(Todo, pk=pk)

#     todo.completed = not todo.completed
#     todo.save()

#     event_type = (
#         TodoEvent.TODO_CHECKED
#         if todo.completed
#         else TodoEvent.TODO_UNCHECKED
#     )

#     TodoEvent.objects.create(
#         todo=todo,
#         event_type=event_type,
#         details={'completed': todo.completed}
#     )


#     return render(request, 'partials/todo_item.html', {'todo': todo})

# def edit_todo(request, pk):
#     todo = get_object_or_404(Todo, pk=pk)
#     if request.method == 'GET':
#         return render(request, 'partials/todo_edit_form.html', {'todo': todo})
#     title = request.POST.get('title', '').strip()
#     description = request.POST.get('description', '').strip()
#     if not title:
#         return JsonResponse({'error': 'Title required'}, status=400)
#     if Todo.objects.exclude(pk=todo.pk).filter(title__iexact=title).exists():
#         return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
    
#     if todo.title.lower() == title.lower() and todo.description == description:
#         return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        
#     old = {'title': todo.title, 'description': todo.description}
#     todo.title = title
#     todo.description = description
#     todo.save()
#     TodoEvent.objects.create(todo=todo, event_type=TodoEvent.TODO_UPDATED, details={'old': old, 'new': {'title': title, 'description': description}})
   
#     return render(request, 'partials/todo_item.html', {'todo': todo})


# def delete_todo(request, pk):
#     todo = get_object_or_404(Todo, pk=pk)
#     TodoEvent.objects.create(todo=todo, event_type=TodoEvent.TODO_DELETED, details={'title': todo.title})
#     todo.delete()
#     todos = Todo.objects.order_by('-created_at')
   
#     return render(request, 'partials/todo_list.html', {'todos': todos})


# def todo_history(request, pk):
#     todo = get_object_or_404(Todo, pk=pk)
#     events = todo.events.all()

#     return render(request, 'partials/todo_history.html', {'todo': todo, 'events': events})

