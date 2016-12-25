from evolution.core.trait import Trait
from evolution.server.card import Card


def test_valid_card():
    card = Card(3, Trait.carnivore)
    assert card.to_json() == [3, 'carnivore']


def test_loc():
    cards = [
        Card(3, Trait.carnivore),
        Card(4, Trait.carnivore),
        Card(-2, Trait.carnivore)
    ]
    assert [card.to_json() for card in cards] == \
           [[3, 'carnivore'], [4, 'carnivore'], [-2, 'carnivore']]
