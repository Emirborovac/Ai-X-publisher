# project/urls.py (main urls.py of your project)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('custom_admin/', include('custom_admin.urls')),  # Use an underscore to match your access path
]
