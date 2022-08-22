from django.contrib import admin

from .models import User, Event


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ['name', 'availability_starts', 'availability_ends']
    list_display = ['name', 'availability_starts', 'availability_ends']
    ordering = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = ['name', 'date', 'starts', 'ends']
    list_display = ('name', 'date', 'starts', 'ends', 'assignee')
    ordering = ['-date', 'starts', 'name']
