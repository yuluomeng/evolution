import copy
import json
import os

from evolution.core.utils import lmap
from evolution.core.trait import Trait
from evolution.server.species import Species
from evolution.server.player import Player
from evolution.server.tests.mock import TestFestProxy
from evolution.server.card import Card
from evolution.server.dealer import Dealer


def feed1_from_file(config_file):
    config = json.load(config_file)
    dealer = dealer_from_json(config)
    dealer.feed1()
    return json.dumps(dealer_to_json(dealer))


def step4_from_file(config_file):
    config, action4 = json.load(config_file)
    dealer = dealer_from_json(config)

    for player, jaction in zip(dealer.players, action4):
        player.proxy.action4 = jaction
        player.proxy.internal_player = player

    dealer.run_turn()
    return json.dumps(dealer_to_json(dealer))


def compare_input_against_output(folder, fn):
    for root, dirs, files in os.walk(folder):
        for file_name in files:
            if file_name.endswith('in.json'):
                with open(os.path.join(root, file_name)) as input_f:
                    output_file_name = file_name.replace('-in.json', '-out.json')
                    with open(os.path.join(root, output_file_name)) as output_f:
                        print(file_name)
                        assert json.loads(fn(input_f)) == json.load(output_f)


def test_fest_10():
    compare_input_against_output('test-fest-10', feed1_from_file)


def test_fest_11():
    compare_input_against_output('test-fest-11', step4_from_file)


def dealer_from_json(jdealer):
    [jplayers, watering_hole, jdeck] = jdealer

    players = lmap(player_from_json, jplayers)
    deck = lmap(card_from_json, jdeck)

    return Dealer(players, watering_hole, deck)


def card_from_json(jcard):
    [food, jtrait] = jcard
    trait = Trait.from_json(jtrait)

    return Card(food, trait)


def player_from_json(jplayer):
    [[_, id], [_, jboards], [_, bag], *cards] = jplayer

    boards = lmap(species_from_json, jboards)
    if cards:
        [_, jcards] = cards[0]
        cards = lmap(card_from_json, jcards)

    proxy = TestFestProxy()

    return Player(id, proxy, boards, bag, cards)


def species_from_json(jspecies):
    [
        [_, food], [_, body], [_, population], [_, jtraits],
        *maybe_fat_food
    ] = jspecies

    traits = lmap(Trait.from_json, jtraits)

    if maybe_fat_food:
        [_, fat_food] = maybe_fat_food[0]
    else:
        fat_food = 0

    return Species(food, body, population, traits, fat_food)


def dealer_to_json(dealer):
    players = [player_to_json(player) for player in dealer.players]
    deck = [card_to_json(card) for card in dealer.deck]
    return [players, dealer.watering_hole, deck]


def player_to_json(player):
    jplayer = [
        ['id', player._id],
        ['species', [species_to_json(species) for species in player.boards]],
        ['bag', player.bag],
    ]
    if player.cards:
        jplayer.append(['cards', [card_to_json(card) for card in player.cards]])
    return jplayer


def species_to_json(species):
    jspecies = [
        ['food', species.food],
        ['body', species.body],
        ['population', species.population],
        ['traits', [trait.to_json() for trait in species.traits]]
    ]
    if species.fat_food > 0:
        jspecies.append(['fat-food', species.fat_food])
    return jspecies


def card_to_json(card):
    return [card.food, card.trait.to_json()]
