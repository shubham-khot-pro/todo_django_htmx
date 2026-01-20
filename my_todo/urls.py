from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Django Allauth URLs
    path('accounts/', include('allauth.urls')),
    
    # Todo app
    path('todos/', include('todo_app.urls')),
    
    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]