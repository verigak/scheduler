# An Django event scheduler

`Events` and `Users` are created from the admin UI.

For each `Event` we generate a bit mask of the 30min intervals that it occupies. For each day we need 48 intervals (0:00-0:30, 0:30-1:00, ... , 23:30-0:00), so the mask will be 48 bits.

Then for each `User` we can bitwise **OR** all assigned events for a day and generate a "busy" mask, marking all intervals that they are busy. To check if a new `Event` conflicts with that `User` we can then bitwise **AND** with the busy mask. If the result is not 0, it means there is a conflict.

Additionally, each `User` has an *availability mask* which is another bit mask marking the times the `User` is available (e.g. 9:00-17:00). This is used in a similar way to further filter down the eligible Users.

When an `Event` is created there is an attempt to assign it to a `User`. If no `User` is available for that day and time, then it stays in the database unassigned.

When a `User` is created (or updated), the assignment algorithm runs again for any unassigned `Events`, possibly assigning them to the new `User`.

## Limitations

* Events can't start or end at more precise times that 30min intervals
* Events can't span multiple days
* No timezones support
