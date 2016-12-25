import unittest

from evolution.core.trait import Trait
from evolution.client.data import Card


class TestCardOrdering(unittest.TestCase):

    def test_ordering_by_trait(self):
        smaller_card = Card(3, Trait.ambush)
        larger_card = Card(-3, Trait.carnivore)

        self.assertTrue(smaller_card < larger_card)

    def test_ordering_by_food(self):
        smaller_card = Card(2, Trait.carnivore)
        larger_card = Card(5, Trait.carnivore)

        self.assertTrue(smaller_card < larger_card)


class TestCardFromJSON(unittest.TestCase):
    def test_valid_card(self):
        jcard = [2, 'carnivore']
        self.assertEqual(Card.from_json(jcard), Card(2, Trait.carnivore))

    def test_card_not_list(self):
        with self.assertRaises(ValueError):
            jcard = 'hello'
            Card.from_json(jcard)

    def test_list_invalid_length(self):
        with self.assertRaises(ValueError):
            jcard = [2, 'carnivore', True]
            Card.from_json(jcard)

    def test_invalid_trait(self):
        with self.assertRaises(ValueError):
            jcard = [4, 45]
            Card.from_json(jcard)

    def test_food_not_int(self):
        with self.assertRaises(ValueError):
            jcard = [True, 'carnivore']
            Card.from_json(jcard)

    def test_invalid_food_value(self):
        with self.assertRaises(ValueError):
            jcard = [10, 'carnivore']
            Card.from_json(jcard)

    def test_invalid_food_value_non_carnivore(self):
        with self.assertRaises(ValueError):
            jcard = [4, 'horns']
            Card.from_json(jcard)