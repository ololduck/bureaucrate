import unittest
from bureaucrate.utils import parse_timespec
from datetime import timedelta


class TestUtils(unittest.TestCase):
    def test_timespec(self):
        d = timedelta(days=-6)
        self.assertEqual(parse_timespec('6d'), d)
        d = timedelta(days=-36, seconds=-630)
        self.assertEqual(parse_timespec('1M 6d 10m 30s'), d)


if __name__ == '__main__':
    unittest.main()
