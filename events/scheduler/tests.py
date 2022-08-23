from datetime import time

from django.test import TestCase

from .models import timerange_to_bitmask, bitmask_to_timerange, all_intervals


class MaskEncodingTests(TestCase):
    def test_roundtrip(self):
        # Try all combinations of (t0, t1) as long as t0 <= t1
        for t0 in all_intervals():
            for t1 in all_intervals():
                if t1 != time() and t1 < t0:
                    continue
                mask = timerange_to_bitmask(t0, t1)
                if t1 != time() and t0 == t1:
                    self.assertEqual(mask, 0)
                    continue

                u0, u1 = bitmask_to_timerange(mask)
                self.assertEqual(t0, u0)
                self.assertEqual(t1, u1)
