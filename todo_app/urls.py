# urls.py
"""
RESTful URL configuration for todo application.
"""

from django.urls import path
from todo_app import views

app_name = "todo_app"

urlpatterns = [
    # Todo CRUD operations
    path('todos/', views.TodoListView.as_view(), name='index'),
    path('todos/create/', views.CreateTodoView.as_view(), name='create'),
    path('todos/<int:pk>/toggle/', views.ToggleTodoView.as_view(), name='toggle'),
    path('todos/<int:pk>/edit/', views.EditTodoView.as_view(), name='edit'),
    path('todos/<int:pk>/soft-delete/', views.SoftDeleteTodoView.as_view(), name='soft_delete'),
    
    # Deleted todos management
    path('todos/deleted/', views.DeletedTodosView.as_view(), name='deleted_todos'),
    path('todos/<int:pk>/restore/', views.RestoreTodoView.as_view(), name='restore'),
    path('todos/<int:pk>/hard-delete/', views.HardDeleteTodoView.as_view(), name='hard_delete'),
    
    # History
    path('todos/<int:pk>/history/', views.TodoHistoryView.as_view(), name='history'),
    
    # Infinite scroll endpoints
    path('todos/load-more/', views.LoadMoreTodosView.as_view(), name='load_more_todos'),
    path('todos/deleted/load-more/', views.LoadMoreDeletedTodosView.as_view(), name='load_more_deleted'),
    path('todos/<int:pk>/history/load-more/', views.LoadMoreHistoryView.as_view(), name='load_more_history'),
    
    # Root redirect
    path('', views.TodoListView.as_view(), name='home'),
]


# from django.contrib import admin
# from django.urls import path, include
# from todo_app import views

# app_name = "todo_app" 

# urlpatterns = [
#     # path('admin/', admin.site.urls),
#     path('', views.index, name='index'),
#     path('create/', views.create_todo , name= 'create'),
#     path('<int:pk>/toggle/', views.toggle_todo, name='toggle'),
#     path('<int:pk>/edit/', views.edit_todo, name='edit'),
#     path('<int:pk>/delete/', views.delete_todo, name='delete'),
#     path('<int:pk>/history/', views.todo_history, name='history'),
# ]
