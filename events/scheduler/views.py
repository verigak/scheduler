from datetime import date, timedelta

from django.shortcuts import get_object_or_404, render

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
    context = {
        'intervals': all_intervals(),
        'rows': rows,
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
    packed = [(rows[i][0], rows[i][1], rows[i+1][1]) for i in range(0, len(rows), 2)]

    context = {
        'user': user,
        'rows': packed,
        'prev': (d - timedelta(days=1)).isoformat(),
        'today': date.today(),
        'next': (d + timedelta(days=1)).isoformat(),
        'current': d.isoformat(),
    }
    return render(request, 'scheduler/user.html', context)
