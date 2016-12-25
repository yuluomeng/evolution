import unittest

from evolution.core.trait import Trait
from evolution.server.action import (
    AddToWateringHole, ReplaceTrait, AddSpecies, AddBody, AddPopulation)
from evolution.server.card import Card
from evolution.server.player import Player
from evolution.server.species import Species
from evolution.server.tests.mock import MockPlayerProxy


class ActionValidationMixin:

    species = Species(food=0, body=0, population=1, traits=[Trait.horns])
    boards = [species, species.copy(), species.copy()]
    cards = [
        Card(1, Trait.carnivore), Card(2, Trait.carnivore),
        Card(3, Trait.carnivore), Card(4, Trait.carnivore)
    ]
    player = Player(
        id=1, proxy=MockPlayerProxy(), boards=boards, bag=0, cards=cards)


class TestAddToWateringHole(unittest.TestCase, ActionValidationMixin):

    def test_valid(self):
        whb_card_index = 3
        self.assertEqual(
            AddToWateringHole.from_json(whb_card_index),
            AddToWateringHole(3))

    def test_not_natural(self):
        whb_card_index = True
        with self.assertRaises(ValueError):
            AddToWateringHole.from_json(whb_card_index)


class TestReplaceTrait(unittest.TestCase, ActionValidationMixin):

    def test_valid(self):
        rt = [0, 0, 0]
        self.assertEqual(
            ReplaceTrait.from_json(rt), ReplaceTrait(0, 0, 0))

    def test_invalid_type(self):
        rt = '[0, 0, 0]'
        with self.assertRaises(ValueError):
            ReplaceTrait.from_json(rt)

    def test_invalid_length(self):
        rt = [0, 0, 0, 0]
        with self.assertRaises(ValueError):
            ReplaceTrait.from_json(rt)

    def test_not_all_natural(self):
        rt = [False, 0, 0]
        with self.assertRaises(ValueError):
            ReplaceTrait.from_json(rt)

    def test_invalid_trait_index(self):
        rt = ReplaceTrait(0, 1, 0)
        with self.assertRaises(ValueError):
            ReplaceTrait._validate_action(rt, self.player)

    def test_invalid_species_index(self):
        rt = ReplaceTrait(3, 0, 0)
        with self.assertRaises(ValueError):
            ReplaceTrait._validate_action(rt, self.player)


class TestAddSpeciesValidation(unittest.TestCase, ActionValidationMixin):

    def test_valid(self):
        bt = [0, 1, 2, 3]
        self.assertEqual(
            AddSpecies.from_json(bt), AddSpecies(0, [1, 2, 3]))

    def test_invalid_type(self):
        bt = True
        with self.assertRaises(ValueError):
            AddSpecies.from_json(bt)

    def test_invalid_length(self):
        bt = [0, 0, [1, 2, 3]]
        with self.assertRaises(ValueError):
            AddSpecies.from_json(bt)

    def test_not_all_natural(self):
        bt = [0, [True, 2, 3]]
        with self.assertRaises(ValueError):
            AddSpecies.from_json(bt)

    def test_no_duplicates(self):
        bt = [0, [0, 1, 2]]
        with self.assertRaises(ValueError):
            AddSpecies.from_json(bt)

    def test_invalid_card_index(self):
        bt = [4, [0, 1, 2]]
        with self.assertRaises(ValueError):
            AddSpecies.from_json(bt)

    def test_invalid_card_index_in_traits(self):

        bt = [0, [1, 2, 4]]
        with self.assertRaises(ValueError):
            AddSpecies.from_json(bt)


class TestAddPopulationValidation(unittest.TestCase, ActionValidationMixin):

    def test_valid(self):
        gp = ['population', 0, 0]
        self.assertEqual(
            AddPopulation.from_json(gp), AddPopulation(0, 0))

    def test_invalid_length(self):
        gp = [0, 0]
        with self.assertRaises(ValueError):
            AddPopulation.from_json(gp)

    def test_invalid_type(self):
        gp = '["population", 0, 0]'
        with self.assertRaises(ValueError):
            AddPopulation.from_json(gp)

    def test_invalid_name(self):
        gp = ['body', 0, 0]
        with self.assertRaises(ValueError):
            AddPopulation.from_json(gp)

    def test_indices_not_natural(self):
        gp = ['population', False, 0]
        with self.assertRaises(ValueError):
            AddPopulation.from_json(gp)

    def test_invalid_species_index(self):
        gp = AddPopulation(3, 0)
        with self.assertRaises(ValueError):
            AddPopulation._validate_action(gp, self.player)


class TestAddBodyValidation(unittest.TestCase, ActionValidationMixin):

    def test_valid(self):
        gb = ['body', 0, 0]
        self.assertEqual(
            AddBody.from_json(gb), AddBody(0, 0))

    def test_invalid_length(self):
        gb = [0, 0]
        with self.assertRaises(ValueError):
            AddBody.from_json(gb)

    def test_invalid_type(self):
        gb = '["body", 0, 0]'
        with self.assertRaises(ValueError):
            AddBody.from_json(gb)

    def test_invalid_name(self):
        gb = ['population', 0, 0]
        with self.assertRaises(ValueError):
            AddBody.from_json(gb)

    def test_indices_not_natural(self):
        gb = ['body', False, 0]
        with self.assertRaises(ValueError):
            AddBody.from_json(gb)

    def test_invalid_species_index(self):
        gb = AddBody(3, 0)
        with self.assertRaises(ValueError):
            AddBody._validate_action(gb, self.player)
