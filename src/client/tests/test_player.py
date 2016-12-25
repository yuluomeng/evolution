from copy import deepcopy
from pytest import raises

from evolution.client.data import Player, Species, Card
from evolution.core.trait import Trait


def test_valid_player():
    jplayer = [3, [], []]

    assert Player.from_json(jplayer) == Player(
        id=1, boards=[], bag=3, cards=[])

    jplayer_plus = deepcopy(jplayer)
    jplayer_plus[2].append([2, 'carnivore'])
    assert Player.from_json(jplayer_plus) == Player(
        id=1, boards=[], bag=3, cards=[Card(food=2, trait=Trait.carnivore)])

    jspecies = [
        ['food', 2],
        ['body', 4],
        ['population', 3],
        ['traits', []]
    ]
    jplayer_with_species = deepcopy(jplayer)
    jplayer_with_species[1].append(jspecies)
    print(jplayer_with_species)
    assert Player.from_json(jplayer_with_species) == Player(
        id=1, boards=[Species(food=2, body=4, population=3, traits=[])],
        bag=3, cards=[])


def test_invalid_player():
    jplayer = [3, [], []]

    jplayer_not_list = True
    with raises(ValueError):
        Player.from_json(jplayer_not_list)

    jplayer_too_long = deepcopy(jplayer).append(True)
    with raises(ValueError):
        Player.from_json(jplayer_too_long)

    jplayer_invalid_species_value = deepcopy(jplayer)
    jplayer_invalid_species_value[1] = ['species', ('horns', )]
    with raises(ValueError):
        Player.from_json(jplayer_invalid_species_value)

    jplayer_invalid_bag_value = deepcopy(jplayer)
    jplayer_invalid_bag_value[0] = True
    with raises(ValueError):
        Player.from_json(jplayer_invalid_bag_value)

    jplayer_invalid_card_value = deepcopy(jplayer)
    jplayer_invalid_card_value[2] = [24, 'carnivore']
    with raises(ValueError):
        Player.from_json(jplayer_invalid_card_value)
