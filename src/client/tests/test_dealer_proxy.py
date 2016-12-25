from pytest import raises

from evolution.client.action import (
    AddToWateringHole, ReplaceTrait, AddSpecies, AddPopulation, AddBody)
from evolution.client.feeding import VegetarianFeeding
from evolution.client.dealer_proxy import (
    BaseDealerProxy, RemoteDealerProxy, Turn)
from evolution.client.data import Card, Player, Species
from evolution.core.trait import Trait


def test_handle_start_turn():

    class MockDealerProxy(RemoteDealerProxy):
        def __init__(self, *args, **kwargs):
            self.current_turn = Turn.unstarted
            self.player_state = Player()

    dealer_proxy = MockDealerProxy()

    start_turn_msg = [2, 3, [], [[3, "carnivore"]]]
    dealer_proxy._handle_start(start_turn_msg)

    new_player = Player(id=1, boards=[], bag=3, cards=[Card(3, Trait.carnivore)])
    assert dealer_proxy.player_state == new_player


def test_serialize_actions():

    actions = {
        AddToWateringHole: AddToWateringHole(2),
        ReplaceTrait: [ReplaceTrait(2, 3, 4)],
        AddSpecies: [AddSpecies(1, [2])],
        AddPopulation: [AddPopulation(1, 2), AddPopulation(3, 4)],
        AddBody: [AddBody(0, 1)]
    }

    action4 = [
        2,
        [['population', 1, 2], ['population', 3, 4]],
        [['body', 0, 1]],
        [[1, 2]],
        [[2, 3, 4]]
    ]

    assert BaseDealerProxy._serialize_actions(actions) == action4


def test_set_player_state():

    watering_hole = 3
    jplayer = [2, [], []]

    dealer_proxy = BaseDealerProxy()
    dealer_proxy._set_player_state(watering_hole, jplayer)

    assert dealer_proxy.player_state == Player(id=1, bag=2)


def test_set_player_state_invalid_watering_hole():

    watering_hole = True
    jplayer = [2, [], []]

    dealer_proxy = BaseDealerProxy()
    with raises(ValueError):
        dealer_proxy._set_player_state(watering_hole, jplayer)


def test_choose_actions():

    before_jopponents = []
    after_jopponents = []

    boards = [Species()]
    cards = [
        Card(1, Trait.ambush),
        Card(1, Trait.carnivore),
        Card(1, Trait.symbiosis),
        Card(1, Trait.fat_tissue),
        Card(1, Trait.horns),
        Card(1, Trait.warning_call),
        Card(1, Trait.foraging)
    ]

    dealer_proxy = BaseDealerProxy()
    dealer_proxy.player_state = Player(id=1, boards=boards, cards=cards)

    expected_actions = {
            AddToWateringHole: AddToWateringHole(0),
            AddPopulation: [AddPopulation(1, 6)],
            AddBody: [AddBody(1, 4)],
            AddSpecies: [AddSpecies(1, [3])],
            ReplaceTrait: [ReplaceTrait(1, 0, 2)]
    }

    assert (
        dealer_proxy._choose_actions(before_jopponents, after_jopponents) ==
        expected_actions)


def test_choose_actions_invalid_opponents():

    before_jopponents = []
    after_jopponents = True

    dealer_proxy = BaseDealerProxy()
    with raises(ValueError):
        dealer_proxy._choose_actions(before_jopponents, after_jopponents)


def test_choose_feeding():

    jspecies = [
        ['food', 0],
        ['body', 0],
        ['population', 1],
        ['traits', []]
    ]

    bag = 0
    jboards = [jspecies]
    jcards = []
    jopponents = []
    watering_hole = 2

    dealer_proxy = BaseDealerProxy()
    assert (
        dealer_proxy._choose_feeding(
            bag, jboards, jcards, watering_hole, jopponents) ==
        VegetarianFeeding(0))


def test_choose_feeding_invalid_bag():

    bag = True
    jboards = jcards = jopponents = []
    watering_hole = 2

    dealer_proxy = BaseDealerProxy()
    with raises(ValueError):
        dealer_proxy._choose_feeding(bag, jboards, jcards, watering_hole, jopponents)


def test_choose_feeding_invalid_jboards():

    bag = 0
    jboards = True
    jcards = jopponents = []
    watering_hole = 2

    dealer_proxy = BaseDealerProxy()
    with raises(ValueError):
        dealer_proxy._choose_feeding(bag, jboards, jcards, watering_hole, jopponents)


def test_choose_feeding_invalid_watering_hole():

    bag = 0
    jboards = jcards = jopponents = []
    watering_hole = True

    dealer_proxy = BaseDealerProxy()
    with raises(ValueError):
        dealer_proxy._choose_feeding(bag, jboards, jcards, watering_hole, jopponents)


def test_validate_next_turn_valid():

    dealer_proxy = BaseDealerProxy()
    assert dealer_proxy._validate_next_turn(Turn.start) is None


def test_validate_next_turn_invalid():

    dealer_proxy = BaseDealerProxy()
    with raises(ValueError):
        assert dealer_proxy._validate_next_turn(Turn.feedNext)
