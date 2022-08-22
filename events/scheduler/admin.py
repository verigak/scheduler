from django import forms
from django.contrib import admin

from .models import User, Event


class UserAdminForm(forms.ModelForm):
    def clean(self):
        starts = self.cleaned_data['availability_starts']
        ends = self.cleaned_data['availability_ends']
        if ends <= starts:
            raise forms.ValidationError({'availability_ends': 'Event must end after start time'})
        if starts.minute not in (0, 30) or starts.second > 0 or starts.microsecond > 0:
            raise forms.ValidationError({'availability_starts': 'Times must be in exact multiples of 30 min'})
        if ends.minute not in (0, 30) or ends.second > 0 or ends.microsecond > 0:
            raise forms.ValidationError({'availability_ends': 'Times must be in exact multiples of 30 min'})


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    fields = ['name', 'availability_starts', 'availability_ends']
    list_display = ['name', 'availability_starts', 'availability_ends']
    ordering = ['name']


class EventAdminForm(forms.ModelForm):
    def clean(self):
        starts = self.cleaned_data['starts']
        ends = self.cleaned_data['ends']
        if ends <= starts:
            raise forms.ValidationError({'ends': 'Event must end after start time'})
        if starts.minute not in (0, 30) or starts.second > 0 or starts.microsecond > 0:
            raise forms.ValidationError({'starts': 'Times must be in exact multiples of 30 min'})
        if ends.minute not in (0, 30) or ends.second > 0 or ends.microsecond > 0:
            raise forms.ValidationError({'ends': 'Times must be in exact multiples of 30 min'})


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    fields = ['name', 'date', 'starts', 'ends']
    list_display = ('name', 'date', 'starts', 'ends', 'assignee')
    ordering = ['-date', 'starts', 'name']
