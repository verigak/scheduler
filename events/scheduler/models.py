# In our models we use bitmasks to represent time ranges, each bit
# representing a 30min interval, for a total of 48 bits to represent
# a full day

import random

from datetime import date, time

from django.core.validators import ValidationError
from django.db import models
from django.db.models import Count, F, Q


# Default availability is 9:00-17:00. Any event outside a user's availability
# is not considered for assignment. The availability mask is generated
# dynamically based on the _starts and _ends values.
class User(models.Model):
    name = models.CharField(max_length=200)
    availability_starts = models.TimeField(default=time(9, 0))
    availability_ends = models.TimeField(default=time(17, 0))
    availability_mask = models.BigIntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.availability_mask = timerange_to_bitmask(self.availability_starts, self.availability_ends)
        super(User, self).save(*args, **kwargs)

        # Try to assign any unassigned events when we add a new user
        for event in Event.objects.filter(date__gte=date.today(), assignee=None):
            user = get_available_user(event.date, event.mask)
            if user:
                event.assignee = user
                event.save()


# Each event belongs to a single day and can only start and end in 30 min
# intervals. On save we generate the mask and try to assign a user (or None
# if no matching user is found)
class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    starts = models.TimeField()
    ends = models.TimeField()
    mask = models.BigIntegerField()
    assignee = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.date})'

    def save(self, *args, **kwargs):
        mask = timerange_to_bitmask(self.starts, self.ends)
        self.mask = mask
        self.assignee = get_available_user(self.date, mask)
        super(Event, self).save(*args, **kwargs)


# This is our scheduling algorithm
def get_available_user(date, mask):
    # Find all users with matching availability
    available = User.objects.annotate(
        availability_match=F('availability_mask').bitand(mask)
    ).filter(availability_match=mask)

    # Find overlapping events
    overlapping = Event.objects.annotate(
        mask_match=F('mask').bitand(mask)
    ).filter(date=date, mask_match__gt=0)

    # User ids that are busy then
    busy_ids = set(e.assignee_id for e in overlapping)

    matches = available.exclude(id__in=busy_ids) \
        .annotate(event_count=Count('event', filter=Q(event__date=date))) \
        .order_by('event_count')

    if matches.count() == 0:
        return None

    count = matches.first().event_count

    # Return a random user from those matching the minimum count
    return random.choice(matches.filter(event_count=count))


def timerange_to_bitmask(t0, t1):
    assert t0 <= t1
    assert t0.minute in (0, 30)
    assert t1.minute in (0, 30)
    assert t0.second == 0
    assert t1.second == 0
    assert t0.microsecond == 0
    assert t1.microsecond == 0

    b0 = t0.hour * 2 + (0 if t0.minute == 0 else 1)
    b1 = t1.hour * 2 + (0 if t1.minute == 0 else 1)
    mask = 0
    for i in range(b0, b1):
        mask |= 1 << i
    return mask


# We assume only one range is encoded in the mask
def bitmask_to_timerange(mask):
    # transform bitmask into a binary array
    b = [mask & (1 << i) != 0 for i in range(48)]

    try:
        i = b.index(True)
    except ValueError:
        return (time(), time())  # No 1 bit found, return Empty reange

    j = b.index(False, i)

    t0 = bitindex_to_time(i)
    t1 = bitindex_to_time(j)
    return (t0, t1)


def bitindex_to_time(i):
    h, m = divmod(i, 2)
    return time(h, 30 if m == 1 else 0)
