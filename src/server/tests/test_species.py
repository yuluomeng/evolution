import unittest
from pytest import raises

from evolution.core.trait import Trait
from evolution.server.species import Species


def test_to_json():
    species = Species(
        food=3, body=3, population=4,
        traits=[Trait.fat_tissue, Trait.horns], fat_food=2)

    jspecies = [
        ['food', 3],
        ['body', 3],
        ['population', 4],
        ['traits', ['fat-tissue', 'horns']],
        ['fat-food', 2]
    ]
    assert species.to_json() == jspecies

    species_no_fat_food = species.copy()
    species_no_fat_food.fat_food = 0
    jspecies_no_fat_food = jspecies[:4]
    assert species_no_fat_food.to_json() == jspecies_no_fat_food


def test_hunger():
    species = Species(food=1, body=1, population=5, traits=[Trait.carnivore])
    assert species.hunger() == 4

    species_not_hungry = Species(food=1, body=1, population=1, traits=[])
    assert species_not_hungry.hunger() == 0


def test_fat_food_need():
    species_no_fat_tissue = Species(food=1, body=1, population=5, traits=[])
    assert species_no_fat_tissue.fat_food_need() == 0

    species_with_fat_tissue = Species(
        food=1, body=3, population=5, traits=[Trait.fat_tissue])
    assert species_with_fat_tissue.fat_food_need() == 3

    species_with_fat_tissue_and_fat_food = Species(
        food=1, body=3, population=5, fat_food=2, traits=[Trait.fat_tissue])
    assert species_with_fat_tissue_and_fat_food.fat_food_need() == 1


def test_try_eat():
    species_before = Species(food=1, body=1, population=6, traits=[])
    species_after = species_before.copy()
    species_before.try_eat(10)
    species_after.food = 2
    assert species_before == species_after


def test_try_eat_species_full():
    species_before = Species(food=1, body=1, population=1, traits=[])
    species_after = species_before.copy()
    species_before.try_eat(10)
    assert species_before == species_after


def test_try_eat_foraging():
    species_before = Species(
        food=1, body=1, population=6, traits=[Trait.foraging])
    species_after = species_before.copy()
    species_before.try_eat(10)
    species_after.food = 3
    assert species_before == species_after


def test_try_eat_limited_by_watering_hole():
    species_before = Species(
        food=1, body=1, population=6, traits=[Trait.foraging])
    species_after = species_before.copy()
    species_before.try_eat(1)
    species_after.food = 2
    assert species_before == species_after


def test_try_eat_limited_by_species_hunger():
    species_before = Species(
        food=1, body=1, population=2, traits=[Trait.foraging])
    species_after = species_before.copy()
    species_before.try_eat(10)
    species_after.food = 2
    assert species_before == species_after


def test_try_take_fat_food_no_fat_tissue():
    species = Species(food=1, body=1, population=6, traits=[])
    with raises(AssertionError):
        species.try_take_fat_food(tokens=2, watering_hole=3)


def test_try_take_fat_food_watering_hole_less_than_tokens_requested():
    species_before = Species(
        food=1, body=6, population=6, traits=[Trait.fat_tissue])
    species_after = species_before.copy()
    species_before.try_take_fat_food(tokens=6, watering_hole=3)
    species_after.fat_food = 3
    assert species_before == species_after


def test_try_take_fat_food_watering_hole_more_than_tokens_requested():
    species_before = Species(
        food=1, body=6, population=6, traits=[Trait.fat_tissue])
    species_after = species_before.copy()
    species_before.try_take_fat_food(tokens=3, watering_hole=6)
    species_after.fat_food = 3
    assert species_before == species_after


def test_replace_trait():
    species_with_fat_food = Species(
        food=1, body=6, population=6, traits=[Trait.fat_tissue], fat_food=2)
    species_with_fat_food.replace_trait(0, Trait.carnivore)

    new_species = Species(
        food=1, body=6, population=6, traits=[Trait.carnivore])
    assert species_with_fat_food == new_species


def test_food_bag_transfer():
    species_with_food = Species(food=3, body=6, population=6, traits=[])
    assert species_with_food.food_bag_transfer() == 3

    new_species = Species(food=0, body=6, population=6, traits=[])
    assert species_with_food == new_species


class TraitTest(object):
    def test_is_protected_by_neighbor(self):
        self.assertEqual(
            self.defender._protected_by_neighbor(
                self.attacker._as_attacker(), self.lneighbor, self.rneighbor),
            self.is_protected_by_neighbor)

    def test_is_self_protected(self):
        self.assertEqual(
            self.defender._protects_self(
                self.attacker._as_attacker(), self.lneighbor, self.rneighbor),
            self.is_self_protected)

    def test_is_attackable(self):
        self.assertEqual(
            self.defender.is_attackable(
                self.attacker, self.lneighbor, self.rneighbor),
            self.is_attackable)


class TestCarnivoreIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestAmbushIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.ambush])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestBurrowingIsAttackableWhenFoodNotEqualToPopulation(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=2, traits=[Trait.burrowing])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestBurrowingIsNotAttackableWhenFoodEqualToPopulation(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.burrowing])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestClimbingPreventsAttackIfTraitCarnivoreDoesNotHaveClimbing(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.climbing])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestClimbingDoesNotPreventAttackIfCarnivoreHasClimbing(
        TraitTest, unittest.TestCase):
    attacker = Species(
        food=1, body=1, population=1, traits=[Trait.carnivore, Trait.climbing])
    defender = Species(food=1, body=1, population=1, traits=[Trait.climbing])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestCooperationIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(
        food=1, body=1, population=1, traits=[Trait.cooperation])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestFatTissueIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestFertileIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.fertile])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestForagingIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.foraging])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestHardShellProtectsAgainstAttackerBodyWithinFour(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=3, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.hard_shell])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestHardShellDoesNotProtectAgainstAttackerBodyEqualToFour(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=5, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.hard_shell])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestHardShellDoesNotProtectAgainstAttackerBodyFourGreater(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=7, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.hard_shell])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestHerdingProtectsAgainstSmallerSpeciesPopulations(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=3, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=5, traits=[Trait.herding])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestHerdingProtectsAgainstEqualSpeciesPopulations(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=3, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=3, traits=[Trait.herding])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestHerdingDoesNotProtectAgainstGreaterSpeciesPopulations(
        TraitTest,  unittest.TestCase):
    attacker = Species(food=1, body=1, population=5, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=3, traits=[Trait.herding])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestHornsIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.horns])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestLongNeckIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.long_neck])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestPackHuntingIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(
        food=1, body=1, population=1, traits=[Trait.pack_hunting])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestScavengerIsAttackable(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.scavenger])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestSymbiosisProtectsIfRightNeighborHasLargerBodyThanDefender(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.symbiosis])
    lneighbor = False
    rneighbor = Species(food=1, body=5, population=1, traits=[Trait.herding])

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestSymbiosisDoesNotProtectIfRightNeighborHasEqualBodyToDefender(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=1, population=1, traits=[Trait.symbiosis])
    lneighbor = False
    rneighbor = Species(food=1, body=1, population=1, traits=[Trait.herding])

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestSymbiosisDoesNotProtectIfRightNeighborHasSmallerBodyThanDefender(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=5, population=1, traits=[Trait.symbiosis])
    lneighbor = False
    rneighbor = Species(food=1, body=1, population=1, traits=[Trait.herding])

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestSymbiosisWithoutRightNeighbor(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=5, population=1, traits=[Trait.symbiosis])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestWarningCallOnLeftNeighborProtectsAttack(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=5, population=1, traits=[])
    lneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])
    rneighbor = False

    is_protected_by_neighbor = True
    is_self_protected = False
    is_attackable = False


class TestWarningCallOnRightNeighborProtectsAttack(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=5, population=1, traits=[])
    lneighbor = False
    rneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])

    is_protected_by_neighbor = True
    is_self_protected = False
    is_attackable = False


class TestWarningCallOnBothNeighborProtectsAttack(
        TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(food=1, body=5, population=1, traits=[])
    lneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])
    rneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])

    is_protected_by_neighbor = True
    is_self_protected = False
    is_attackable = False


class TestWarningCallOnLeftNeighborAgainstAttackerWithAmbush(
        TraitTest, unittest.TestCase):
    attacker = Species(
        food=1, body=1, population=1, traits=[Trait.carnivore, Trait.ambush])
    defender = Species(food=1, body=5, population=1, traits=[])
    lneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestWarningCallOnRightNeighborAgainstAttackerWithAmbush(
        TraitTest, unittest.TestCase):
    attacker = Species(
        food=1, body=1, population=1, traits=[Trait.carnivore, Trait.ambush])
    defender = Species(food=1, body=5, population=1, traits=[])
    lneighbor = False
    rneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestWarningCallOnBothNeighborAgainstAttackerWithAmbush(
        TraitTest, unittest.TestCase):
    attacker = Species(
        food=1, body=1, population=1, traits=[Trait.carnivore, Trait.ambush])
    defender = Species(food=1, body=5, population=1, traits=[])
    lneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])
    rneighbor = Species(
        food=1, body=1, population=1, traits=[Trait.warning_call])

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True


class TestMultipleTraitsOnDefender(TraitTest, unittest.TestCase):
    attacker = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    defender = Species(
        food=1, body=5, population=1,
        traits=[Trait.long_neck, Trait.hard_shell])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestPackHuntingAndHardShell(TraitTest, unittest.TestCase):
    attacker = Species(
        food=2, body=3, population=4,
        traits=[Trait.carnivore, Trait.pack_hunting])
    defender = Species(food=2, body=2, population=1, traits=[Trait.hard_shell])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = False
    is_attackable = True

    def test_attacker_body_is_reset(self):
        self.defender.is_attackable(
            self.attacker, self.lneighbor, self.rneighbor)
        self.assertEqual(self.attacker.body, 3)


class TestPackHuntingAndHardShellOnDefender(TraitTest, unittest.TestCase):
    attacker = Species(food=2, body=3, population=4, traits=[Trait.carnivore])
    defender = Species(
        food=2, body=2, population=1,
        traits=[Trait.hard_shell, Trait.pack_hunting])
    lneighbor = False
    rneighbor = False

    is_protected_by_neighbor = False
    is_self_protected = True
    is_attackable = False


class TestReplaceTrait(unittest.TestCase):
    def test_replace_fat_tissue(self):
        fat_tissue_species = Species(
            food=1, body=1, population=1,
            traits=[Trait.fat_tissue], fat_food=2)
        fat_tissue_species.replace_trait(0, Trait.horns)

        self.assertEqual(
            fat_tissue_species,
            Species(food=1, body=1, population=1, traits=[Trait.horns])
        )

    def test_replace_fat_tissue_with_fat_tissue(self):
        fat_tissue_species = Species(
            food=1, body=1, population=1, traits=[Trait.fat_tissue],
            fat_food=2)
        fat_tissue_species.replace_trait(0, Trait.fat_tissue)

        self.assertEqual(
            fat_tissue_species,
            Species(
                food=1, body=1, population=1, traits=[Trait.fat_tissue],
                fat_food=2))
