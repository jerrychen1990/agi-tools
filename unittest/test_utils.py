import math
from unittest import TestCase

from agit.utils import cal_vec_similarity


# unitt test
class TestUtils(TestCase):
    def test_cal_vec_similarity(self):
        vec1 = [1, 2, 3]
        vec2 = [2, 4, 6]
        sim = cal_vec_similarity(vec1, vec2)
        self.assertEqual(sim, 1.0)
        dist = cal_vec_similarity(vec1, vec2, metric="l2_disntance")
        self.assertEqual(dist, 0.0)
        dist = cal_vec_similarity(
            vec1, vec2, normalize=False, metric="l2_disntance")
        self.assertEqual(dist, math.sqrt(14))
