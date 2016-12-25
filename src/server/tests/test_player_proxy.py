from pytest import raises

from evolution.server.action import (
    AddToWateringHole, ReplaceTrait, AddSpecies, AddPopulation, AddBody)
from evolution.server.feeding import(
    NoFeeding, VegetarianFeeding, FatTissueFeeding, CarnivoreFeeding)
from evolution.server.player_proxy import BasePlayerProxy


def test_deserialize_action4():

    action4 = [
        2,
        [['population', 1, 2], ['population', 3, 4]],
        [['body', 0, 1]],
        [[1, 2]],
        [[2, 3, 4]]
    ]

    whb_action = AddToWateringHole(2)
    actions = [
        AddSpecies(1, [2]),
        ReplaceTrait(2, 3, 4),
        AddPopulation(1, 2),
        AddPopulation(3, 4),
        AddBody(0, 1)
    ]

    assert (
        BasePlayerProxy._deserialize_action4(action4) ==
        (whb_action, actions))


def test_deserialize_feeding():

    assert BasePlayerProxy._deserialize_feeding(False) == NoFeeding()
    assert BasePlayerProxy._deserialize_feeding(1) == VegetarianFeeding(1)
    assert (
        BasePlayerProxy._deserialize_feeding([2, 3]) == FatTissueFeeding(2, 3))
    assert (
        BasePlayerProxy._deserialize_feeding([2, 3, 4]) ==
        CarnivoreFeeding(2, 3, 4))


def test_deserialize_invalid_feeding():

    with raises(ValueError):
        BasePlayerProxy._deserialize_feeding([1, 2, 3, 4])
