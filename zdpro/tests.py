from django.test import TestCase

# Create your tests here.
from zdpro.middleware.timer import *

class module(TestCase):
    def test_timer(self):
        mytimer = Timer()
        mytimer.run()
        @mytimer.add()
        def _test(tmp,interval=10):
            print tmp
        _test('abc',interval=5)


