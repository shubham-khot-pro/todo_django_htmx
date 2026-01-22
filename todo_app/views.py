from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.views import LogoutView as AuthLogoutView
from .models import Todo, TodoEvent

class TodoListView(TemplateView):
    """
    Display paginated list of active todo items.
    """
    template_name = 'todo_list.html'
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        per_page = 5
        
        # Only get todos for the current logged-in user
        print("Request Object:")
        print(self.request)
        print(self.request.META)
        print(self.request.headers)
        print(self.request.GET)
        print("----------------------------------------------------------------------------------------------------")
        print("Current User:")
        print(self.request.user)

        todos = Todo.objects.active().filter(user=self.request.user).order_by('-created_at')
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
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=403)
        
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        # Check for duplicate title for this user only
        if Todo.objects.active().filter(user=request.user, title__iexact=title).exists():
            return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        
        # Create todo with the current user
        print("Creating todo for user:", request.user)
        print("User ID:", request.user.id)
        print("title:", title )
        todo = Todo.objects.create(
            title=title, 
            description=description,
            user=request.user,  # Assign the current user
            status='pending'  # Default status
        )
        # Create event with the current user
        # TodoEvent.objects.create(
        #     user=request.user,  # Assign the current user
        #     todo=todo,
        #     event_type=TodoEvent.TODO_CREATED,
        #     details={'title': title}
        # )

        
        if request.htmx:
            # Return the new todo item
            return render(request, 'partials/todo_item.html', {'todo': todo})
        return redirect('todo_app:index')


class ToggleTodoView(View):
    """
    Toggle completion status of a todo item.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        # Only allow toggling todos that belong to the current user
        todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
        todo.completed = not todo.completed
        todo.save()
        
        # event_type = (
        #     TodoEvent.TODO_CHECKED
        #     if todo.completed
        #     else TodoEvent.TODO_UNCHECKED
        # )
        
        # TodoEvent.objects.create(
        #     user=request.user,  # Assign the current user
        #     todo=todo,
        #     event_type=event_type,
        #     details={'completed': todo.completed, 'title': todo.title}
        # )
        
        return render(request, 'partials/todo_item.html', {'todo': todo})


class EditTodoView(View):
    """
    Handle editing of todo items.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, pk):
        # Only allow editing todos that belong to the current user
        todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
        return render(request, 'partials/todo_edit_form.html', {'todo': todo})
    
    def post(self, request, pk):
        # Only allow editing todos that belong to the current user
        todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            return JsonResponse({'error': 'Title required'}, status=400)
        
        # Check for duplicate title for this user only (excluding current todo)
        if Todo.objects.active().filter(user=request.user).exclude(pk=todo.pk).filter(title__iexact=title).exists():
            return JsonResponse({'error': 'A todo with this title already exists'}, status=400)
        
        if todo.title.lower() == title.lower() and todo.description == description:
            return JsonResponse({'error': 'No changes detected'}, status=400)
        
        old_data = {'title': todo.title, 'description': todo.description}
        
        # Task 5: Use ORM update method for better performance instead of save()

        # so 2 methods 
        # 1] -  todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
        #       todo.title = title
        #       todo.description = description
        #       todo.save()
        # 2] - below code
        # Todo.objects.filter(pk=todo.pk).update(
        #     title=title,
        #     description=description,
        #     updated_at=timezone.now()
        # )
        # Refresh the todo object from database
        # reloads fresh values from DB into todo instance 
        # todo.refresh_from_db()


        # 3] - using signals as in signals.py file
        todo._current_user = request.user  # Attach user for signal
        todo.title = title
        todo.description = description
        todo.save()
        # This will trigger the signal to log the update event
        
        
        
        # TodoEvent.objects.create(
        #     user=request.user,  # Assign the current user
        #     todo=todo,
        #     event_type=TodoEvent.TODO_UPDATED,
        #     details={
        #         'old': old_data,
        #         'new': {'title': title, 'description': description}
        #     }
        # )
        
        return render(request, 'partials/todo_item.html', {'todo': todo})


class SoftDeleteTodoView(View):
    """
    Soft delete a todo item.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        # Only allow deleting todos that belong to the current user
        todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
        
        todo.soft_delete()
        # this have save() which will trigger signal
        
        # TodoEvent.objects.create(
        #     user=request.user,  # Assign the current user
        #     todo=todo,
        #     event_type=TodoEvent.TODO_DELETED,
        #     details={'title': todo.title}
        # )
        
        if request.htmx:
            # Return empty div to remove the todo from DOM
            return render(request, 'partials/empty.html')
        return redirect('todo_app:index')


class DeletedTodosView(TemplateView):
    """
    Display list of soft-deleted todo items with pagination.
    """
    template_name = 'deleted_todos.html'
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        per_page = 5
        
        # Only get deleted todos for the current user
        todos = Todo.objects.deleted().filter(user=self.request.user).order_by('-deleted_at')
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
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        # Only allow restoring todos that belong to the current user
        todo = get_object_or_404(Todo.objects.deleted().filter(user=request.user), pk=pk)
        
        todo.restore()
        # this have save() which will trigger signal
        
        # todo.refresh_from_db()
        
        # TodoEvent.objects.create(
        #     user=request.user,  # Assign the current user
        #     todo=todo,
        #     event_type=TodoEvent.TODO_RESTORED,
        #     details={'title': todo.title}
        # )
        
        if request.htmx:
            # Return empty to remove from deleted list
            return render(request, 'partials/empty.html')
        return redirect('todo_app:deleted_todos')


class HardDeleteTodoView(View):
    """
    Permanently delete a todo item and all associated events.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        # Only allow hard deleting todos that belong to the current user
        todo = get_object_or_404(Todo.objects.deleted().filter(user=request.user), pk=pk)
        
        # Log event before deletion
        TodoEvent.objects.create(
            user=request.user,  # Assign the current user
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
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, pk):
        # Only allow viewing history for todos that belong to the current user
        todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
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


class LoadMoreTodosView(View):
    """
    Load more todos with infinite scroll.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        page = int(request.GET.get('page', 2))
        per_page = 5
        
        # Only get todos for the current user
        todos = Todo.objects.active().filter(user=request.user).order_by('-created_at')
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
    Load more deleted todos with infinite scroll.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        page = int(request.GET.get('page', 2))
        per_page = 5
        
        # Only get deleted todos for the current user
        todos = Todo.objects.deleted().filter(user=request.user).order_by('-deleted_at')
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
    Load more history events with infinite scroll.
    """
    
    @method_decorator(login_required(login_url='/accounts/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, pk):
        # Only allow loading more history for todos that belong to the current user
        todo = get_object_or_404(Todo.objects.active().filter(user=request.user), pk=pk)
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


# class LogoutView(AuthLogoutView):
#     """Custom logout view"""
#     next_page = '/'