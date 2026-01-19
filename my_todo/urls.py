# my_todo/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from todo_app import views as todo_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # Simple home page
    path('todos/', include('todo_app.urls')),  # Your existing todo URLs
    path('oauth/', include('social_django.urls', namespace='social')),  # Google OAuth
    path('logout/', todo_views.LogoutView.as_view(), name='logout'),  # Logout
]