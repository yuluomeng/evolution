import unittest

from evolution.core.trait import Trait
from evolution.client.action import (
    AddBody, AddPopulation, ReplaceTrait, AddSpecies, AddToWateringHole)
from evolution.client.data import Card, Player, Species, Opponent
from evolution.client.feeding import (
    NoFeeding, CarnivoreFeeding, VegetarianFeeding, FatTissueFeeding)
from evolution.client.strategy import (
    play_cards, choose_target, feed_fat_tissue, feed_vegetarian,
    feed_carnivore, feedNext)


class TestChooseFeeding(unittest.TestCase):

    def test_no_species(self):
        player = Player(id=1, boards=[], bag=0, cards=[])
        self.assertEquals(feedNext(player, 2, [player, player]),
                          NoFeeding())

    def test_all_species_not_hungry(self):
        vegetarian = Species(
            food=2, body=2, population=2, traits=[], fat_food=0)
        player = Player(id=1, boards=[vegetarian], bag=0, cards=[])
        self.assertEquals(feedNext(player, 2, [player, player]),
                          NoFeeding())

    def test_feed_fat_tissue_before_vegetarian(self):
        fat_tissue = Species(
            food=2, body=4, population=2, traits=[Trait.fat_tissue],
            fat_food=1)
        vegetarian = Species(
            food=1, body=2, population=2, traits=[Trait.fat_tissue],
            fat_food=0)
        player = Player(id=1, boards=[fat_tissue, vegetarian], bag=0, cards=[])
        self.assertEqual(feedNext(player, 2, [player, player]),
                         FatTissueFeeding(0, 2))

    def test_feed_vegetarian_before_carnivore(self):
        vegetarian = Species(
            food=1, body=2, population=2, traits=[], fat_food=0)
        carnivore = Species(
            food=2, body=2, population=2, traits=[Trait.carnivore, ],
            fat_food=0)
        player = Player(id=1, boards=[carnivore, vegetarian], bag=0, cards=[])
        self.assertEqual(feedNext(player, 2, [player, player]),
                         VegetarianFeeding(1))

    def test_feed_fat_tissue_before_carnivore_attacks(self):
        carnivore = Species(
            food=1, body=2, population=2,
            traits=[Trait.carnivore, Trait.fat_tissue], fat_food=0)
        vegetarian = Species(
            food=2, body=2, population=2, traits=[], fat_food=0)
        player1 = Player(id=1, boards=[vegetarian, carnivore], bag=0, cards=[])
        player2 = Player(id=2, boards=[carnivore], bag=0, cards=[])
        player3 = Player(id=3, boards=[vegetarian], bag=0, cards=[])
        self.assertEqual(
             feedNext(player1, 7, [player2, player3]),
             FatTissueFeeding(1, 2))

    def test_feed_carnivore(self):
        vegetarian = Species(
            food=2, body=2, population=2, traits=[])
        carnivore = Species(
            food=1, body=2, population=2, traits=[Trait.carnivore])
        opponent1 = Opponent([vegetarian, carnivore])
        opponent2 = Opponent([carnivore])
        opponent3 = Opponent([vegetarian])
        self.assertEqual(
            feedNext(opponent1, 7, [opponent2, opponent3]),
            CarnivoreFeeding(1, 1, 0))

    def test_carnivore_must_attack_own_opponent(self):
        vegetarian = Species(
            food=2, body=2, population=2, traits=[], fat_food=0)
        carnivore = Species(
            food=1, body=2, population=2, traits=[Trait.carnivore], fat_food=0)
        unattackable = Species(
            food=1, body=2, population=2, traits=[Trait.climbing])
        opponent1 = Opponent([vegetarian, carnivore])
        opponent2 = Opponent([unattackable])
        opponent3 = Opponent([unattackable])
        self.assertEqual(
            feedNext(opponent1, 2, [opponent2, opponent3]),
            NoFeeding())

    def test_carnivore_not_permanently_mutated_with_pack_hunting(self):
        attacker = Species(
            food=1, body=3, population=2,
            traits=[Trait.carnivore, Trait.pack_hunting], fat_food=0)
        defender1 = Species(
            food=1, body=2, population=2, traits=[Trait.hard_shell],
            fat_food=0)
        defender2 = Species(
            food=1, body=1, population=2, traits=[Trait.hard_shell],
            fat_food=0)
        player = Opponent([attacker])
        opponent1 = Opponent([defender1])
        opponent2 = Opponent([defender2])
        self.assertEqual(
            feedNext(player, 76, [opponent1, opponent2]),
            CarnivoreFeeding(0, 1, 0))


class TestChooseFatTissueFeeding(unittest.TestCase):

    def test_no_species(self):
        los = []
        self.assertIsNone(feed_fat_tissue(los, 2))

    def test_no_fat_tissue_species(self):
        los = [Species(food=2, body=2, population=3, traits=[], fat_food=0)]
        self.assertIsNone(feed_fat_tissue(los, 2))

    def test_one_hungry_species(self):
        species1 = Species(
            food=2, body=2, population=3, traits=[Trait.fat_tissue],
            fat_food=0)
        los = [species1, ]
        self.assertEqual(feed_fat_tissue(los, 2),
                         FatTissueFeeding(0, 2))

    def test_multiple_hungry_species_with_same_hunger(self):
        species1 = Species(
            food=2, body=2, population=3, traits=[Trait.fat_tissue],
            fat_food=0)
        species2 = Species(
            food=4, body=3, population=5, traits=[Trait.fat_tissue],
            fat_food=0)
        los = [species1, species2]
        self.assertEqual(feed_fat_tissue(los, 4),
                         FatTissueFeeding(1, 3))

    def test_multiple_hungry_species_with_same_hunger_and_attributes(self):
        species1 = Species(
            food=2, body=2, population=3,
            traits=[Trait.fat_tissue, Trait.horns], fat_food=0)
        species2 = Species(
            food=2, body=2, population=3, traits=[Trait.fat_tissue],
            fat_food=0)
        los = [species1, species2]
        self.assertEqual(feed_fat_tissue(los, 2),
                         FatTissueFeeding(0, 2))

    def test_watering_hole_tokens_less_than_requested_tokens(self):
        species1 = Species(
            food=2, body=2, population=5, traits=[Trait.fat_tissue],
            fat_food=0)
        los = [species1]
        self.assertEqual(feed_fat_tissue(los, 2),
                         FatTissueFeeding(0, 2))

    def test_species_with_existing_fat_food(self):
        species1 = Species(
            food=2, body=2, population=5, traits=[Trait.fat_tissue],
            fat_food=1)
        los = [species1]
        self.assertEqual(feed_fat_tissue(los, 2),
                         FatTissueFeeding(0, 1))


class TestFeedVegetarian(unittest.TestCase):
    def test_no_species(self):
        los = []
        self.assertIsNone(feed_vegetarian(los))

    def test_no_vegetarian_species(self):
        species1 = Species(
            food=2, body=2, population=3, traits=[Trait.carnivore], fat_food=0)
        los = [species1, ]
        self.assertIsNone(feed_vegetarian(los))

    def test_one_vegetarian_species(self):
        species1 = Species(food=2, body=2, population=3, traits=[], fat_food=0)
        los = [species1, ]
        self.assertEqual(feed_vegetarian(los), VegetarianFeeding(0))

    def test_multiple_vegetarian_species(self):
        species1 = Species(food=2, body=2, population=3, traits=[], fat_food=0)
        species2 = Species(food=3, body=4, population=6, traits=[], fat_food=0)
        los = [species1, species2]
        self.assertEqual(feed_vegetarian(los), VegetarianFeeding(1))

    def test_multiple_vegetarians_equally_large(self):
        species1 = Species(food=3, body=3, population=4, traits=[], fat_food=0)
        species2 = Species(
            food=3, body=3, population=4, traits=[Trait.horns], fat_food=0)
        los = [species1, species2]
        self.assertEqual(feed_vegetarian(los), VegetarianFeeding(0))


class TestFeedCarnivore(unittest.TestCase):
    def setUp(self):
        self.species1 = Species(
            food=4, body=3, population=4, traits=[Trait.carnivore])
        self.species2 = Species(
            food=3, body=3, population=4, traits=[Trait.carnivore])
        self.species3 = Species(
            food=5, body=3, population=5, traits=[Trait.carnivore])
        self.species4 = Species(
            food=5, body=3, population=5, traits=[Trait.climbing])

        self.opponent1 = Opponent([self.species1])
        self.opponent2 = Opponent([self.species2])
        self.opponent3 = Opponent([self.species1])
        self.opponent4 = Opponent([self.species3])
        self.opponent5 = Opponent([self.species4])
        self.opponent6 = Opponent([])

    def test_no_hungry_carnivores(self):
        self.assertIsNone(
            feed_carnivore([self.species1], [self.opponent1, self.opponent1]))

    def test_one_target(self):
        self.assertEqual(
            feed_carnivore([self.species2], [self.opponent1, self.opponent3]),
            CarnivoreFeeding(0, 0, 0))

    def test_multiple_targets(self):
        self.assertEqual(
            feed_carnivore(
                [self.species2],
                [self.opponent1, self.opponent3, self.opponent4]),
            CarnivoreFeeding(0, 2, 0))

    def test_all_species_not_attackable(self):
        self.assertIsNone(
            feed_carnivore(
                [self.species2],
                [self.opponent5, self.opponent5, self.opponent5]))

    def test_other_opponent_has_no_target(self):
        self.assertEqual(
            feed_carnivore(
                [self.species2], [self.opponent1, self.opponent6]),
            CarnivoreFeeding(0, 0, 0))


class TestChooseTarget(unittest.TestCase):

    def setUp(self):
        self.attacker1 = Species(
            food=7, body=7, population=7, traits=[Trait.carnivore])

        self.defender1 = Species(
            food=1, body=1, population=1, traits=[Trait.climbing])
        self.defender2 = Species(food=2, body=1, population=1, traits=[])
        self.defender3 = Species(food=2, body=1, population=3, traits=[])
        self.defender4 = Species(
            food=2, body=2, population=3, traits=[Trait.symbiosis])

        self.opponent1 = Opponent([])
        self.opponent2 = Opponent([self.defender1])
        self.opponent3 = Opponent([self.defender2, self.defender3])
        self.opponent4 = Opponent([self.defender2, self.defender4])

    def test_no_species_in_player(self):
        self.assertEqual(
            choose_target(self.attacker1, self.opponent1),
                         (None, None))

    def test_all_species_not_attackable(self):
        self.assertEqual(choose_target(self.attacker1, self.opponent2),
                         (None, None))

    def test_species_defended_by_neighbor(self):
        self.assertEqual(choose_target(self.attacker1, self.opponent4),
                         (self.defender4, 1))

    def test_second_species_is_larger(self):
        self.assertEqual(choose_target(self.attacker1, self.opponent3),
                         (self.defender3, 1))


class SillyMixin:
    @classmethod
    def setup_class(cls):
        cls.player = Player(id=1, boards=cls.boards, cards=cls.cards, bag=0)

    def test_actions(cls):
        jaction4 = play_cards(cls.player, [], [])
        assert jaction4 == cls.expected_card_plays


class TestCardPlaysOneBoard(SillyMixin):
    @classmethod
    def setup_class(cls):
        cls.cards = [
            Card(1, Trait.ambush),
            Card(1, Trait.carnivore),
            Card(1, Trait.symbiosis),
            Card(1, Trait.fat_tissue),
            Card(1, Trait.horns),
            Card(1, Trait.warning_call),
            Card(1, Trait.foraging)
        ]

        cls.boards = [Species()]

        cls.expected_card_plays = {
            AddToWateringHole: AddToWateringHole(0),
            AddPopulation: [AddPopulation(1, 6)],
            AddBody: [AddBody(1, 4)],
            AddSpecies: [AddSpecies(1, [3])],
            ReplaceTrait: [ReplaceTrait(1, 0, 2)]
        }
        cls.expected_remaining_cards = [Card(1, Trait.warning_call)]

        super().setup_class()
