import unittest
from pytest import raises

from evolution.client.data import Species
from evolution.core.trait import Trait


class TestOrdering(unittest.TestCase):
    def setUp(self):
        self.species1 = Species(
            food=2, body=2, population=2, traits=[], fat_food=0)
        self.species2 = Species(
            food=1, body=1, population=1, traits=[], fat_food=0)
        self.species3 = Species(
            food=3, body=1, population=2, traits=[], fat_food=0)
        self.species4 = Species(
            food=1, body=3, population=1, traits=[], fat_food=0)

    def sort_los(self, los):
        """Sort the los in descending order."""

        return sorted(los, reverse=True)

    def test_sort_based_on_population(self):
        orig_los = [self.species2, self.species1]
        sorted_los = [self.species1, self.species2]
        self.assertEqual(self.sort_los(orig_los), sorted_los)

    def test_sort_based_on_food(self):
        orig_los = [self.species2, self.species3]
        sorted_los = [self.species3, self.species2]
        self.assertEqual(self.sort_los(orig_los), sorted_los)

    def test_sort_based_on_body(self):
        orig_los = [self.species2, self.species4]
        sorted_los = [self.species4, self.species2]
        self.assertEqual(self.sort_los(orig_los), sorted_los)

    def test_sort_longer_list(self):
        orig_los = [self.species1, self.species2, self.species3, self.species4]
        sorted_los = [
            self.species3, self.species1, self.species4, self.species2
        ]
        self.assertEqual(self.sort_los(orig_los), sorted_los)


def test_valid_from_json():
    jspecies = [
        ['food', 2],
        ['body', 4],
        ['population', 3],
        ['traits', []]
    ]
    assert Species.from_json(jspecies) == Species(
        food=2, body=4, population=3, traits=[])

    jspecies_fat_food_zero = [
        ['food', 2],
        ['body', 4],
        ['population', 3],
        ['traits', []],
        ['fat-food', 0]
    ]
    assert Species.from_json(jspecies_fat_food_zero) == Species(
        food=2, body=4, population=3, traits=[])

    fatty_jspecies = [
        ['food', 2],
        ['body', 4],
        ['population', 3],
        ['traits', ['fat-tissue']],
        ['fat-food', 1]
    ]
    assert Species.from_json(fatty_jspecies) == Species(
        food=2, body=4, population=3, traits=[Trait.fat_tissue], fat_food=1)


def test_invalid_from_json():
    jspecies = [
        ['food', 2],
        ['body', 4],
        ['population', 3],
        ['traits', []]
    ]

    bool_jspecies = True
    with raises(ValueError):
        Species.from_json(bool_jspecies)

    jspecies_too_long = jspecies + [True, True]
    with raises(ValueError):
        Species.from_json(jspecies_too_long)

    jspecies_property_not_list = list(jspecies)
    jspecies_property_not_list[0] = True
    with raises(ValueError):
        Species.from_json(jspecies_property_not_list)

    jspecies_property_invalid_len = list(jspecies)
    jspecies_property_invalid_len[0].append(True)
    with raises(ValueError):
        Species.from_json(jspecies_property_invalid_len)

    jspecies_not_food = list(jspecies)
    jspecies_not_food[0] = ['invalid-prop', 2]
    with raises(ValueError):
        Species.from_json(jspecies_not_food)

    jspecies_food_not_nat = list(jspecies)
    jspecies_food_not_nat[0] = ['food', 2.0]
    with raises(ValueError):
        Species.from_json(jspecies_food_not_nat)

    jspecies_not_population = list(jspecies)
    jspecies_not_population[1] = ['invalid-prop', 2]
    with raises(ValueError):
        Species.from_json(jspecies_not_population)

    jspecies_population_not_nat = list(jspecies)
    jspecies_population_not_nat[1] = ['population', 2.0]
    with raises(ValueError):
        Species.from_json(jspecies_population_not_nat)

    jspecies_not_body = list(jspecies)
    jspecies_not_body[2] = ['invalid-prop', 2]
    with raises(ValueError):
        Species.from_json(jspecies_not_body)

    jspecies_body_not_nat = list(jspecies)
    jspecies_body_not_nat[2] = ['body', 2.0]
    with raises(ValueError):
        Species.from_json(jspecies_body_not_nat)

    jspecies_not_traits = list(jspecies)
    jspecies_not_traits[3] = ['invalid-prop', []]
    with raises(ValueError):
        Species.from_json(jspecies_not_traits)

    jspecies_traits_not_list = list(jspecies)
    jspecies_traits_not_list[3] = ['traits', ()]
    with raises(ValueError):
        Species.from_json(jspecies_traits_not_list)

    jspecies_traits_invalid_len = list(jspecies)
    jspecies_traits_invalid_len[3] = ['traits', [1, 2, 3, 4]]
    with raises(ValueError):
        Species.from_json(jspecies_traits_invalid_len)

    jspecies_traits_invalid_trait = list(jspecies)
    jspecies_traits_invalid_trait[3] = ['traits', ['invalid_trait']]
    with raises(ValueError):
        Species.from_json(jspecies_traits_invalid_trait)

    jspecies_not_fat_food = list(jspecies)
    jspecies_not_fat_food.append(['invalid-prop', 1])
    with raises(ValueError):
        Species.from_json(jspecies_not_fat_food)

    jspecies_fat_food_not_nat = list(jspecies)
    jspecies_fat_food_not_nat.append(['fat-food', 1.0])
    with raises(ValueError):
        Species.from_json(jspecies_fat_food_not_nat)

    jspecies_fat_food_no_fat_tissue = list(jspecies)
    jspecies_fat_food_no_fat_tissue.append(['fat-food', 3])
    with raises(ValueError):
        Species.from_json(jspecies_fat_food_no_fat_tissue)

    jspecies_extinct = list(jspecies)
    jspecies_extinct[2] = ['population', 0]
    with raises(ValueError):
        Species.from_json(jspecies_extinct)

    jspecies_duplicate_traits = list(jspecies)
    jspecies_duplicate_traits[3] = ['traits', ['horns', 'horns']]
    with raises(ValueError):
        Species.from_json(jspecies_duplicate_traits)
