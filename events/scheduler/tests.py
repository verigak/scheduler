from datetime import time

from django.test import TestCase

from .models import timerange_to_bitmask, bitmask_to_timerange


class MaskEncodingTests(TestCase):
    def test_roundtrip(self):
        # Try all combinations of (t0, t1) as long as t0 <= t1
        for t0 in all_times():
            for t1 in all_times():
                if t1 < t0:
                    continue
                mask = timerange_to_bitmask(t0, t1)
                if t0 == t1:
                    self.assertEqual(mask, 0)
                    continue

                u0, u1 = bitmask_to_timerange(mask)
                self.assertEqual(t0, u0)
                self.assertEqual(t1, u1)


def all_times():
    for h in range(24):
        for m in (0, 30):
            yield time(h, m)
