import unittest
from starts_ends_with import StartsEndsWith

test_prefix_list = ['Mg', 'megabyte', 'me', 'Kb', 'overl', 'foo']
test_suffix_list = ['/s', ' per sec', ' per minute', ' / min', 'ps', 'rlap', 'bar']

class TestStartsEndsWith(unittest.TestCase):
    def test_suffix(self):
        sew = StartsEndsWith(suffixes=test_suffix_list)
        self.assertEqual(('-foo', 'bar'), sew('-foobar'))

    def test_prefix(self):
        sew = StartsEndsWith(prefixes=test_prefix_list)
        self.assertEqual(('foo', 'bar-'), sew('foobar-'))

    def test_prefix_suffix(self):
        sew = StartsEndsWith(prefixes=test_prefix_list, suffixes=test_suffix_list)
        self.assertEqual(('foo', None, 'bar'), sew('foobar'))
        self.assertEqual(('foo', ' blah ', 'bar'), sew('foo blah bar'))

    def test_for_best_match(self):
        sew = StartsEndsWith(prefixes=test_prefix_list)
        self.assertEqual(('megabyte', 'able'), sew('megabyteable'))
        self.assertEqual(('me', 'gabyt'), sew('megabyt'))

    def test_for_no_match(self):
        sew = StartsEndsWith(prefixes=test_prefix_list)
        self.assertEqual((None, 'blah'), sew('blah'))

    def test_with_overlap_overlap_allowed(self):
        sew = StartsEndsWith(prefixes=test_prefix_list, suffixes=test_suffix_list)
        self.assertEqual(('overl', 'rlap'), sew('overlap', allow_overlap=True))

    def test_with_overlap_overlap_disallowed_prefix_pri(self):
        sew = StartsEndsWith(prefixes=test_prefix_list, suffixes=test_suffix_list)
        self.assertEqual(('overl', 'ap', None), sew('overlap'))

    def test_with_overlap_overlap_disallowed_suffix_pri(self):
        sew = StartsEndsWith(prefixes=test_prefix_list, suffixes=test_suffix_list)
        self.assertEqual((None, 'ove', 'rlap'), sew('overlap', prefix_priority=False))

    def test_for_caps_insenstitive(self):
        sew = StartsEndsWith(prefixes=test_prefix_list, case_insensitive=True)
        self.assertEqual(('Megabyte', '/SeC'), sew('Megabyte/SeC'))

