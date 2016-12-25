import unittest

from evolution.core import utils


class TestIsNatural(unittest.TestCase):
    def test_is_natural(self):
        self.assertTrue(utils.is_natural(7))

    def test_is_natural_lower_bound(self):
        self.assertTrue(utils.is_natural(0))

    def test_is_natural_float(self):
        self.assertFalse(utils.is_natural(1.0))

    def test_is_natural_negative(self):
        self.assertFalse(utils.is_natural(-1))

    def test_is_natural_bool(self):
        self.assertFalse(utils.is_natural(True))


class TestIsNaturalPlus(unittest.TestCase):
    def test_is_natural_plus_too_low(self):
        self.assertFalse(utils.is_natural_plus(0))

    def test_is_natural_plus(self):
        self.assertTrue(utils.is_natural_plus(7))

    def test_is_natural_plus_float(self):
        self.assertFalse(utils.is_natural_plus(1.0))

    def test_is_natural_plus_negative(self):
        self.assertFalse(utils.is_natural_plus(-1))

    def test_is_natural_plus_bool(self):
        self.assertFalse(utils.is_natural_plus(True))


class TestGetNeighbors(unittest.TestCase):
    def setUp(self):
        self.boards = [1, 2, 3, 4]

    def test_no_left_neighbor(self):
        l_neighbor, r_neighbor = utils.get_neighbors(self.boards, 0)
        self.assertIsNone(l_neighbor, None)
        self.assertEqual(r_neighbor, 2)

    def test_no_right_neighbor(self):
        l_neighbor, r_neighbor = utils.get_neighbors(self.boards, 3)
        self.assertEqual(l_neighbor, 3)
        self.assertIsNone(r_neighbor)

    def test_both_left_and_right_neighbor(self):
        l_neighbor, r_neighbor = utils.get_neighbors(self.boards, 1)
        self.assertEqual(l_neighbor, 1)
        self.assertEqual(r_neighbor, 3)

    def test_invalid_index(self):
        with self.assertRaises(IndexError):
            utils.get_neighbors(self.boards, 8)
