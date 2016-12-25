import unittest

from pytest import raises

from evolution.core.trait import Trait
from evolution.server.action import (
    AddToWateringHole, AddBody, AddPopulation, AddSpecies, ReplaceTrait)
from evolution.server.card import Card
from evolution.server.exception import CheatingPlayerException
from evolution.server.feeding import (
    VegetarianFeeding, CarnivoreFeeding, FatTissueFeeding)
from evolution.server.player import Player
from evolution.server.species import Species

from evolution.server.tests.mock import (
    MockPlayerProxy, MockProxyPlayerWithActions, MockProxyPlayerWithFeeding)


def test_player_to_json():
    species = Species(food=2, body=4, population=3, traits=[])
    player = Player(
        id=2, proxy=MockPlayerProxy(), boards=[species], bag=3,
        cards=[Card(2, Trait.carnivore)])

    jspecies = [
        ['food', 2],
        ['body', 4],
        ['population', 3],
        ['traits', []]
    ]
    jplayer = [3, [jspecies], [[2, 'carnivore']]]
    assert player.to_json() == jplayer


def test_move_food_to_bag():
    one_food = Species(food=1, body=1, population=1, traits=[])
    two_food = Species(food=2, body=1, population=4, traits=[])
    four_food = Species(food=4, body=1, population=4, traits=[])
    before_player = Player(
        id=2, proxy=MockPlayerProxy(), boards=[one_food, two_food, four_food],
        bag=3)
    after_player = before_player.copy()

    before_player.move_food_to_bag()

    after_player.bag = 10
    for species in after_player.boards:
        species.food = 0

    assert before_player == after_player


def test_score():
    one_pop = Species(food=1, body=1, population=1, traits=[Trait.carnivore])
    two_pop = Species(food=2, body=1, population=4, traits=[])
    four_pop = Species(food=4, body=1, population=4, traits=[])
    player = Player(
        id=2, proxy=MockPlayerProxy(), boards=[one_pop, two_pop, four_pop],
        bag=3)

    assert player.score() == 13


def test_remove_extinct():
    extinct = Species(food=0, body=1, population=0, traits=[])
    not_extinct = Species(food=2, body=1, population=4, traits=[])
    before_player = Player(
        id=2, proxy=MockPlayerProxy(),
        boards=[extinct, not_extinct, not_extinct.copy(), extinct.copy()],
        bag=3)

    after_player = before_player.copy()
    assert before_player.remove_extinct() == 2

    after_player.boards = [not_extinct.copy(), not_extinct.copy()]
    assert before_player == after_player


def test_player_card_indices():
    cards = [Card(2, Trait.horns), Card(3, Trait.horns), Card(-1, Trait.horns)]
    player = Player(
        id=1, proxy=MockPlayerProxy(), cards=cards)

    assert player.player_hand_indices() == {0, 1, 2}


def test_invalid_feeding_choice():

    species = Species(food=2, body=1, population=4, traits=[])
    boards = [species, species.copy(), species.copy()]
    proxy = MockProxyPlayerWithFeeding(CarnivoreFeeding(0, 0, 0))
    player = Player(id=1, proxy=proxy, boards=boards)

    with raises(CheatingPlayerException):
        player.feedNext(3, [player.copy(), player.copy()])


def test_end_turn():
    species = Species(food=2, body=1, population=4, traits=[])
    before_player = Player(
        id=2, proxy=MockPlayerProxy(),
        boards=[species, species.copy(), species.copy()], bag=3)
    after_player = before_player.copy()

    before_player.end_turn()

    after_species = Species(food=0, body=1, population=2, traits=[])
    after_player.boards = [
        after_species, after_species.copy(), after_species.copy()]
    after_player.bag = 9

    assert before_player == after_player


class PlayCardsMixin:
    @classmethod
    def setup_class(cls):
        proxy = MockProxyPlayerWithActions(cls.actions)
        cards = [
            Card(1, Trait.horns),
            Card(1, Trait.carnivore),
            Card(1, Trait.ambush)
        ]
        traits = [Trait.fat_tissue, Trait.foraging]
        species = Species(food=0, population=1, body=0, traits=traits)
        cls.before_player = Player(
            id=1, proxy=proxy,
            boards=[species], cards=cards, bag=0)
        cls.after_player = cls.before_player.copy()

    def test_apply_actions(self):
        before_players = []
        after_players = [self.before_player.copy(), self.before_player.copy()]
        assert (self.before_player.play_cards(before_players, after_players) ==
                self.watering_hole_tokens)
        assert self.before_player == self.after_player


class TestPlayCardChoiceNotInHand(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = AddToWateringHole(3), []
        super().setup_class()

    def test_apply_actions(self):
        with raises(CheatingPlayerException):
            super().test_apply_actions()


class TestPlayCardWithDuplicateCardsRaises(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = (
            AddToWateringHole(0),
            [
                AddBody(0, 1),
                AddBody(0, 1)
            ])
        super().setup_class()

        cls.watering_hole_tokens = 1
        cls.after_player.boards[0].body += 2
        cls.after_player.cards = []

    def test_apply_actions(self):
        with raises(CheatingPlayerException):
            super().test_apply_actions()


class TestPlayCardsEmpty(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = AddToWateringHole(0), []
        super().setup_class()

        cls.watering_hole_tokens = 1
        cls.after_player.cards.pop(0)


class TestPlayCardsAddBodies(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = AddToWateringHole(0), [AddBody(0, 1), AddBody(0, 2)]
        super().setup_class()

        cls.watering_hole_tokens = 1
        cls.after_player.boards[0].body += 2
        cls.after_player.cards = []


class TestPlayCardsAddPopulation(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = (
            AddToWateringHole(0),
            [AddPopulation(0, 1), AddPopulation(0, 2)])

        super().setup_class()

        cls.watering_hole_tokens = 1
        cls.after_player.boards[0].population += 2
        cls.after_player.cards = []


class TestPlayCardsReplaceTrait(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = (
            AddToWateringHole(0),
            [ReplaceTrait(0, 0, 1), ReplaceTrait(0, 1, 2)])
        super().setup_class()

        cls.watering_hole_tokens = 1
        cls.after_player.traits = [Trait.fat_tissue, Trait.foraging]
        cls.after_player.cards = []


class TestPlayCardsAddSpeciesWithoutTraits(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = AddToWateringHole(0), [AddSpecies(1, [])]
        super().setup_class()

        cls.watering_hole_tokens = 1
        del cls.after_player.cards[:2]
        cls.after_player.boards.append(
            Species(food=0, population=1, body=0, traits=[]))


class TestPlayCardsAddSpeciesWithTraits(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = AddToWateringHole(0), [AddSpecies(1, [2, 3])]
        super().setup_class()

        cls.before_player.cards.append(Card(1, Trait.fat_tissue))

        cls.watering_hole_tokens = 1
        cls.after_player.cards = []
        cls.after_player.boards.append(
            Species(
                food=0, population=1, body=0,
                traits=[Trait.ambush, Trait.fat_tissue]))


class TestPlayCardMultipleActionTypes(PlayCardsMixin):
    @classmethod
    def setup_class(cls):
        cls.actions = (
            AddToWateringHole(0),
            [
                AddBody(0, 1),
                AddPopulation(0, 2),
                AddSpecies(3, []),
                ReplaceTrait(0, 0, 4)
            ])
        super().setup_class()

        cls.before_player.cards.extend([
            Card(1, Trait.fat_tissue),
            Card(1, Trait.symbiosis),
        ])

        cls.watering_hole_tokens = 1
        cls.after_player.cards = []
        species = cls.after_player.boards[0]
        species.traits[0] = Trait.symbiosis
        species.population += 1
        species.body += 1
        cls.after_player.boards.append(
            Species(food=0, population=1, body=0, traits=[]))


class BasePlayerTest:
    def setUp(self):
        self.before_player = Player(
            id=1, proxy=MockPlayerProxy(), boards=[], bag=10)
        self.after_player = self.before_player.copy()


class TestReducePopulation(BasePlayerTest, unittest.TestCase):
    def test_works(self):
        before_species = Species(food=2, body=3, population=3, traits=[])
        self.before_player.boards.append(before_species)

        self.before_player.reduce_population(0)

        after_species = Species(food=2, body=3, population=2, traits=[])
        self.after_player.boards.append(after_species)

        self.assertEqual(self.before_player, self.after_player)

    def test_species_food_reduced_to_population(self):
        before_species = Species(food=3, body=3, population=3, traits=[])
        self.before_player.boards.append(before_species)

        self.before_player.reduce_population(0)

        after_species = Species(food=2, body=3, population=2, traits=[])
        self.after_player.boards.append(after_species)

        self.assertEqual(self.before_player, self.after_player)


class TestGetFeedingChoices(BasePlayerTest, unittest.TestCase):
    def test_no_species(self):
        opponents = [self.before_player.copy(), self.before_player.copy()]
        self.assertEqual(
            self.before_player.get_feeding_choices(10, opponents), set())

    def test_no_tokens_at_watering_hole(self):
        species = Species(
            food=1, body=2, population=3, traits=[Trait.fat_tissue])
        self.before_player.boards.append(species)

        opponents = [self.before_player.copy(), self.before_player.copy()]
        self.assertEqual(
            self.before_player.get_feeding_choices(0, opponents), set())

    def test_fat_tissue_choices(self):
        species = Species(
            food=1, body=2, population=3, traits=[Trait.fat_tissue])
        self.before_player.boards.append(species)

        opponents = [self.before_player.copy(), self.before_player.copy()]
        choices = {
            FatTissueFeeding(0, 1), FatTissueFeeding(0, 2), VegetarianFeeding(0)
        }
        self.assertEqual(
            self.before_player.get_feeding_choices(10, opponents), choices)

    def test_carnivore_choices(self):
        species = Species(
            food=1, body=2, population=3, traits=[Trait.carnivore])
        self.before_player.boards.append(species)

        opponents = [self.before_player.copy(), self.before_player.copy()]
        choices = {
            CarnivoreFeeding(0, 0, 0), CarnivoreFeeding(0, 1, 0)
        }
        self.assertEqual(
            self.before_player.get_feeding_choices(10, opponents), choices)


class TestAttackableBoards(BasePlayerTest, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.attacker = Species(
            food=1, body=2, population=3, traits=[Trait.carnivore])

    def test_no_species_attackable(self):
        self.assertEqual(
            self.before_player.attackable_boards(self.attacker), [])

    def test_species_attackable(self):
        species = Species(food=2, body=3, population=3, traits=[Trait.horns])
        self.before_player.boards.extend(
            [species, species.copy(), species.copy()])

        attack_options = [0, 1, 2]
        self.assertEqual(
            self.before_player.attackable_boards(self.attacker),
            attack_options)
