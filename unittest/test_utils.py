import math
from unittest import TestCase

from agit.utils import ConfigMixin, cal_vec_similarity


# unitt test
class TestUtils(TestCase):
    def test_cal_vec_similarity(self):
        vec1 = [1, 2, 3]
        vec2 = [2, 4, 6]
        sim = cal_vec_similarity(vec1, vec2)
        self.assertEqual(sim, 1.0)
        dist = cal_vec_similarity(vec1, vec2, metric="l2_distance")
        self.assertEqual(dist, 0.0)
        dist = cal_vec_similarity(
            vec1, vec2, normalize=False, metric="l2_distance")
        self.assertEqual(dist, math.sqrt(14))


    def test_config_mixin(self):
        class TmpCls(ConfigMixin):
            def __init__(self, a, b=3) -> None:
                super().__init__()
                self.a=a
                

                self.b=b
        config = dict(a=2,b=4)
        instance = TmpCls.from_config(config)
        self.assertEqual(2,instance.a)
        
        
        
        