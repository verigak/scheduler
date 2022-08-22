from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('scheduler/', include('scheduler.urls')),
    path('admin/', admin.site.urls),
]
