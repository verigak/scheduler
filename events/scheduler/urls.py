from django.urls import path

from . import views

urlpatterns = [
    path('', views.day, name='index'),
    path('<str:day>', views.day, name='day'),
    path('user/<int:uid>', views.user, name='user'),
    path('user/<int:uid>/<str:day>', views.user, name='user-day'),
    path('generate/<str:day>', views.generate_event, name='generate-day'),
]
