import random

from datetime import date, time, timedelta

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import User, Event, all_intervals 


def day(request, day=''):
    try:
        d = date.fromisoformat(day)
    except ValueError:
        d = date.today()

    users = User.objects.order_by('name')
    rows = []
    for user in users:
        intervals = []
        event_mask = 0
        for event in Event.objects.filter(date=d, assignee=user):
            event_mask |= event.mask
        for i in range(48):
            if user.availability_mask & (1<<i) == 0:
                intervals.append(None)
            elif event_mask & (1<<i) != 0:
                intervals.append('BUSY')
            else:
                intervals.append('FREE')
        rows.append({'user': user, 'intervals': intervals})

    unassigned = Event.objects.filter(date=d, assignee=None).order_by('starts', 'ends', 'name')

    context = {
        'intervals': all_intervals(),
        'rows': rows,
        'unassigned': unassigned,
        'prev': (d - timedelta(days=1)).isoformat(),
        'today': date.today(),
        'next': (d + timedelta(days=1)).isoformat(),
        'current': d.isoformat(),
    }
    return render(request, 'scheduler/day.html', context)

def user(request, uid, day=''):
    user = get_object_or_404(User, pk=uid)

    try:
        d = date.fromisoformat(day)
    except ValueError:
        d = date.today()

    events = Event.objects.filter(date=d, assignee=uid).order_by('starts')
    current_event = None

    rows = []
    for (i, interval) in enumerate(all_intervals()):
        if user.availability_mask & (1<<i) == 0:
            rows.append((interval, None))
        else:
            name = ''
            for event in events:
                if event.mask & (1<<i) != 0:
                    if event != current_event:
                        name = event.name
                        current_event = event
                    else:
                        name = '.'  # Use . to avoid repeating the same name
                    break
            rows.append((interval, name))

    # Pack 2 intervals per row for a more compact layout
    packed = [(rows[i][0], rows[i][1], rows[i+1][1]) for i in range(0, len(rows)-1, 2)]

    context = {
        'user': user,
        'rows': packed,
        'prev': (d - timedelta(days=1)).isoformat(),
        'today': date.today(),
        'next': (d + timedelta(days=1)).isoformat(),
        'current': d.isoformat(),
    }
    return render(request, 'scheduler/user.html', context)


# Generates a random event of arbitrary duration
@require_http_methods(['POST'])
@csrf_exempt
def generate_event(request, day=''):
    try:
        d = date.fromisoformat(day)
    except ValueError:
        # Use a random day in one of the next 7 days
        d = date.today() + timedelta(days=random.randint(1, 7))
    
    starts, ends = sorted(random.sample(list(all_intervals()), 2))
    event = Event(name='Random Event', date=d, starts=starts, ends=ends)
    event.save()
    print(f'Generated event: {event}')
    return HttpResponse(f'Generated Event for {d}: {starts}-{ends}\n')


# Generates an hourly random event
@require_http_methods(['POST'])
@csrf_exempt
def generate_hourly_event(request, day=''):
    try:
        d = date.fromisoformat(day)
    except ValueError:
        # Use a random day in one of the next 7 days
        d = date.today() + timedelta(days=random.randint(1, 7))
    
    h = random.randint(0, 23)
    starts = time(h)
    ends = time(h+1) if h < 23 else time()
    event = Event(name='Random Hourly Event', date=d, starts=starts, ends=ends)
    event.save()
    print(f'Generated event: {event}')
    return HttpResponse(f'Generated Event for {d}: {starts}-{ends}\n')
