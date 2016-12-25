from collections import Counter

from evolution.core.trait import Trait
from evolution.server.card import Card
from evolution.server.dealer import Dealer
from evolution.server.feeding import (
    NoFeeding, FatTissueFeeding, VegetarianFeeding, CarnivoreFeeding)
from evolution.server.player import Player
from evolution.server.species import Species
from evolution.server.tests.mock import (
    MockPlayerProxy, MockCheatingPlayer, MockCardPlayPlayer)


def test_give_cards():

    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
    ]
    watering_hole = 4
    deck = [
        Card(2, Trait.cooperation), Card(4, Trait.carnivore),
        Card(3, Trait.carnivore), Card(1, Trait.horns)
    ]
    dealer = Dealer(players=players, watering_hole=watering_hole, deck=deck)
    player_to_receive_cards = players[1].copy()

    dealer.give_cards(players[1], 2)
    player_to_receive_cards.cards = [
        Card(2, Trait.cooperation), Card(4, Trait.carnivore)
    ]
    updated_deck = [Card(3, Trait.carnivore), Card(1, Trait.horns)]
    assert player_to_receive_cards == dealer.players[1]
    assert updated_deck == dealer.deck


def test_remove_extinct():

    species = Species(food=0, body=1, population=0, traits=[Trait.fat_tissue])
    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[species], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
    ]
    watering_hole = 4
    deck = [
        Card(2, Trait.cooperation), Card(4, Trait.carnivore),
        Card(3, Trait.carnivore), Card(1, Trait.horns)
    ]
    player_with_extinct_species = players[0].copy()
    dealer = Dealer(players=players, watering_hole=watering_hole, deck=deck)

    dealer.remove_extinct(players[0])

    player_with_extinct_species.boards = []
    player_with_extinct_species.cards = [
        Card(2, Trait.cooperation), Card(4, Trait.carnivore)
    ]
    assert player_with_extinct_species == dealer.players[0]

    updated_deck = [Card(3, Trait.carnivore), Card(1, Trait.horns)]
    assert updated_deck == dealer.deck


def test_handle_play_cards():

    players = [
        MockCardPlayPlayer(),
        MockCardPlayPlayer(),
        MockCardPlayPlayer()
    ]
    before_dealer = Dealer(players=players, watering_hole=0, deck=[])
    before_dealer.handle_play_cards()

    after_players = [
        MockCardPlayPlayer(),
        MockCardPlayPlayer(),
        MockCardPlayPlayer()
    ]
    after_dealer = Dealer(players=after_players, watering_hole=9, deck=[])

    assert before_dealer == after_dealer


def test_make_deck():

    deck = Dealer._make_deck()
    trait_counter = Counter(card.trait for card in deck)

    assert trait_counter.pop(Trait.carnivore) == 17
    assert all(value == 7 for value in trait_counter.values())
    assert deck[0] == Card(-3, Trait.ambush)
    assert deck[-1] == Card(3, Trait.warning_call)


def test_rotate_current_player():

    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=4, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=5, proxy=MockPlayerProxy(), boards=[], bag=5),
    ]

    dealer = Dealer(players=players, watering_hole=0, deck=[])
    dealer.current_feeding_index = 4
    dealer._increment_feeding_index()

    assert dealer.current_feeding_index == 0


def test_move_first_player_to_last():

    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=4, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=5, proxy=MockPlayerProxy(), boards=[], bag=5),
    ]

    before_dealer = Dealer(players=players, watering_hole=0, deck=[])
    before_dealer._move_first_player_to_last()

    ordered_players = [
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=4, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=5, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
    ]
    after_dealer = Dealer(players=ordered_players, watering_hole=0, deck=[])
    assert before_dealer == after_dealer


def test_feeding_order():

    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=4, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=5, proxy=MockPlayerProxy(), boards=[], bag=5),
    ]

    dealer = Dealer(players=players, watering_hole=0, deck=[])
    dealer.current_feeding_index = 2

    ordered_players = [
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=4, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=5, proxy=MockPlayerProxy(), boards=[], bag=5),
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
    ]
    assert dealer._feeding_order() == ordered_players


def test_handle_cheating_player_play_cards():
    players = [
        MockCheatingPlayer(),
        MockCheatingPlayer(),
    ]
    before_dealer = Dealer(players=players)
    after_dealer = Dealer(players=[])

    before_dealer.handle_play_cards()
    assert before_dealer == after_dealer


def test_handle_cheating_player_feedNext():
    players = [
        MockCheatingPlayer(),
        MockCheatingPlayer(),
    ]
    before_dealer = Dealer(players=players, watering_hole=1)
    after_dealer = Dealer(players=[], watering_hole=1)

    before_dealer.handle_feeding()
    assert before_dealer == after_dealer


def test_is_game_over():
    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5)
    ]

    deck = [Card(1, Trait.horns), Card(2, Trait.horns), Card(3, Trait.horns),
            Card(1, Trait.climbing), Card(2, Trait.climbing),
            Card(3, Trait.climbing), Card(1, Trait.symbiosis),
            Card(2, Trait.symbiosis)]
    dealer = Dealer(players=players, watering_hole=0, deck=deck)
    assert dealer._is_game_over() is True

    deck.append(Card(3, Trait.carnivore))
    assert dealer._is_game_over() is False


def test_start_turn():
    players = [
        Player(id=1, proxy=MockPlayerProxy(), boards=[], bag=4),
        Player(id=2, proxy=MockPlayerProxy(), boards=[], bag=2),
        Player(id=3, proxy=MockPlayerProxy(), boards=[], bag=5),
    ]
    deck = [
        Card(0, Trait.cooperation), Card(1, Trait.cooperation),
        Card(2, Trait.cooperation), Card(3, Trait.cooperation),
        Card(0, Trait.carnivore), Card(1, Trait.carnivore),
        Card(2, Trait.carnivore), Card(3, Trait.carnivore),
        Card(0, Trait.horns), Card(1, Trait.horns),
        Card(2, Trait.horns), Card(3, Trait.horns),
    ]
    before_dealer = Dealer(
        players=players, watering_hole=2, deck=deck)

    after_players = [player.copy() for player in players]
    for player in after_players:
        player.boards.append(Species())

    after_players[0].cards = [
        Card(0, Trait.cooperation), Card(1, Trait.cooperation),
        Card(2, Trait.cooperation), Card(3, Trait.cooperation),
    ]
    after_players[1].cards = [
        Card(0, Trait.carnivore), Card(1, Trait.carnivore),
        Card(2, Trait.carnivore), Card(3, Trait.carnivore),
    ]
    after_players[2].cards = [
        Card(0, Trait.horns), Card(1, Trait.horns),
        Card(2, Trait.horns), Card(3, Trait.horns),
    ]

    before_dealer.start_turn()
    after_dealer = Dealer(players=after_players, watering_hole=2, deck=[])
    assert before_dealer == after_dealer


class BaseTestFeeding:
    @classmethod
    def setup_class(cls):

        class MockInternalPlayer(Player):
            def __eq__(self, other):
                return (isinstance(other, Player) and
                        self._id == other._id and
                        self.boards == other.boards and
                        self.bag == other.bag and
                        self.cards == other.cards)

            def feedNext(self, *args):
                return cls.feeding

        cls.player1 = MockInternalPlayer(
            id=1, proxy=MockPlayerProxy(), boards=[], bag=1)
        cls.player2 = MockInternalPlayer(
            id=2, proxy=MockPlayerProxy(), boards=[], bag=1)
        cls.player3 = MockInternalPlayer(
            id=3, proxy=MockPlayerProxy(), boards=[], bag=1)

    def test_compare_dealer(self):
        self.before_dealer.feed1()
        print(self.before_dealer)
        print()
        print(self.expected_dealer)
        assert self.before_dealer == self.expected_dealer


class TestFatTissueSingleOption(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = FatTissueFeeding(species_index=0, tokens=1)
        super().setup_class()

        species = Species(
            food=1, body=1, population=2, traits=[Trait.fat_tissue])
        cls.player1.boards = [species]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [cls.player1.copy(), cls.player2, cls.player3]
        expected_players[0].boards[0].fat_food = 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=9, deck=[])


class TestVegetarianSingleOption(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        species = Species(food=1, body=1, population=2, traits=[])
        cls.player1.boards = [species]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [cls.player1.copy(), cls.player2, cls.player3]
        expected_players[0].boards[0].food = 2

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=9, deck=[])


class TestCarnivoreSingleOption(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        species = Species(
            food=1, body=1, population=2, traits=[Trait.carnivore])
        cls.player1.boards = [species]
        cls.player2.boards = [species.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 2
        expected_players[1].boards[0].population = 1
        expected_players[1].boards[0].food = 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=9, deck=[])


class TestNoFeedingNothingAttackable(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = NoFeeding()
        super().setup_class()

        species = Species(
            food=1, body=1, population=2, traits=[Trait.carnivore])
        cls.player1.boards = [species, species.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        cls.expected_dealer = Dealer(
            players=players, watering_hole=10, deck=[])


class TestNoFeedingFull(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = NoFeeding()
        super().setup_class()

        species = Species(food=1, body=1, population=1, traits=[])
        cls.player1.boards = [species, species.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        cls.expected_dealer = Dealer(
            players=players, watering_hole=10, deck=[])


class TestFatTissueWhenSpeciesFull(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = NoFeeding()
        super().setup_class()

        species = Species(
            food=2, body=1, population=2, fat_food=1,
            traits=[Trait.fat_tissue])
        cls.player1.boards = [species]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=0, deck=[])
        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3,
        ]

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestHornsAttacked(BaseTestFeeding):
    """Carnivore population reduced after attacking Horns.

    No new food is added to Carnivore since food must be <= population.
    """
    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        attacker = Species(
            food=1, body=1, population=2, traits=[Trait.carnivore])
        defender = Species(
            food=1, body=1, population=3,
            traits=[Trait.horns, Trait.scavenger])
        cls.player1.boards = [attacker]
        cls.player2.boards = [defender]

        players = [cls.player1, cls.player2, cls.player3]
        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 1
        expected_players[0].boards[0].population = 1
        expected_players[1].boards[0].population = 2
        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=10, deck=[])


class TestHornsAttackedByAttackerWithOnePopulation(BaseTestFeeding):
    """Carnivore becomes extinct after attacking Horns with population size 1.

    Defender also loses a population and becomes extinct.
    """

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        attacker = Species(
            food=0, body=1, population=1, traits=[Trait.carnivore])
        defender = Species(
            food=1, body=1, population=1, traits=[Trait.horns])
        cls.player1.boards = [attacker]
        cls.player2.boards = [defender]

        players = [cls.player1, cls.player2, cls.player3]
        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards = []
        expected_players[1].boards = []
        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=10, deck=[])


class TestCooperationChain(BaseTestFeeding):
    """A chain starts if a species and its right neighbor have cooperation."""

    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        cooperative_species = Species(
            food=0, body=1, population=1, traits=[Trait.cooperation])
        cls.player1.boards = [
            cooperative_species,
            cooperative_species.copy(),
            cooperative_species.copy(),
            cooperative_species.copy()
        ]

        players = [cls.player1, cls.player2, cls.player3]
        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3
        ]
        post_feeding = Species(
            food=1, body=1, population=1, traits=[Trait.cooperation])
        expected_players[0].boards = [
            post_feeding,
            post_feeding.copy(),
            post_feeding.copy(),
            post_feeding.copy()
        ]
        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=6, deck=[])


class TestCooperationChainNotEnoughTokensAtWHB(BaseTestFeeding):
    """Feeding ends when there are no more tokens at the WHB. Will pass two
    tokens if the species has foraging and cooperation."""

    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        cooperative_species_with_foraging = Species(
            food=0, body=1, population=2,
            traits=[Trait.cooperation, Trait.foraging])
        cooperative_species = Species(
            food=0, body=1, population=2, traits=[Trait.cooperation])
        cls.player1.boards = [
            cooperative_species_with_foraging,
            cooperative_species,
            cooperative_species.copy(),
            cooperative_species.copy()
        ]

        players = [cls.player1, cls.player2, cls.player3]
        cls.before_dealer = Dealer(players=players, watering_hole=4, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3
        ]
        post_feeding_with_foraging = Species(
            food=2, body=1, population=2,
            traits=[Trait.cooperation, Trait.foraging])
        post_feeding = Species(
            food=1, body=1, population=2, traits=[Trait.cooperation])
        expected_players[0].boards = [
            post_feeding_with_foraging,
            post_feeding.copy(),
            post_feeding.copy(),
            cooperative_species.copy()
        ]
        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestCooperationChainBreaksWhenSpeciesInMiddleIsFull(BaseTestFeeding):
    """Cooperation is only triggered when a species feeds."""

    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        cooperative_species = Species(
            food=0, body=1, population=1, traits=[Trait.cooperation])
        full_cooperative_species = Species(
            food=1, body=1, population=1, traits=[Trait.cooperation])
        cls.player1.boards = [
            cooperative_species,
            cooperative_species.copy(),
            full_cooperative_species,
            cooperative_species.copy()
        ]

        players = [cls.player1, cls.player2, cls.player3]
        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3
        ]
        expected_players[0].boards = [
            full_cooperative_species.copy(),
            full_cooperative_species.copy(),
            full_cooperative_species.copy(),
            cooperative_species.copy(),
        ]
        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=8, deck=[])


class TestForagingVegetarian(BaseTestFeeding):
    """Foraging allows a species to eat twice."""

    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        forager = Species(
            food=1, body=1, population=4, traits=[Trait.foraging])
        cls.player1.boards = [forager]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3
        ]
        expected_players[0].boards[0].food = 3

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=8, deck=[])


class TestForagingScavenger(BaseTestFeeding):
    """Scavenger triggers a species' Foraging trait."""

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        species = Species(
            food=1, body=1, population=2, traits=[Trait.carnivore])
        foraging_scavenger = Species(
            food=1, body=1, population=6,
            traits=[Trait.foraging, Trait.scavenger])
        cls.player1.boards = [species]
        cls.player2.boards = [foraging_scavenger]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 2
        expected_players[1].boards[0].population = 5
        expected_players[1].boards[0].food = 3

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=7, deck=[])


class TestForagingCarnivore(BaseTestFeeding):
    """Carnivore should eat twice from the WHB if it has Foraging."""

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        foraging_carnivore = Species(
            food=1, body=1, population=5,
            traits=[Trait.carnivore, Trait.foraging])
        cls.player1.boards = [foraging_carnivore]
        cls.player2.boards = [foraging_carnivore.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 3
        expected_players[1].boards[0].population = 4

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=8, deck=[])


class TestScavengerCarnivore(BaseTestFeeding):
    """Carnivore should eat twice from WHB if it has Scavenger."""

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        scavenger_carnivore = Species(
            food=1, body=1, population=5,
            traits=[Trait.carnivore, Trait.scavenger])
        defender = Species(
            food=1, body=1, population=2, traits=[Trait.carnivore])
        cls.player1.boards = [scavenger_carnivore]
        cls.player2.boards = [defender]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 3
        expected_players[1].boards[0].population = 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=8, deck=[])


class TestScavengerTriggerdOnOtherPlayers(BaseTestFeeding):
    """Scavenger eats when another Carnivore eats, no matter of who owns it."""

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        scavenger_carnivore = Species(
            food=1, body=1, population=5,
            traits=[Trait.carnivore, Trait.scavenger])
        cls.player1.boards = [scavenger_carnivore]
        cls.player2.boards = [scavenger_carnivore.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=10, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 3
        expected_players[1].boards[0].population = 4
        expected_players[1].boards[0].food = 2

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=7, deck=[])


class TestScavengerCarnivoreCannotEatTwoTokensDueToWHB(BaseTestFeeding):
    """Carnivore can only eat as many tokens as there are on the WHB."""

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        scavenger_carnivore = Species(
            food=1, body=1, population=5,
            traits=[Trait.carnivore, Trait.scavenger])
        cls.player1.boards = [scavenger_carnivore]
        cls.player2.boards = [scavenger_carnivore.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=1, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 2
        expected_players[1].boards[0].population = 4

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestScavengerCarnivoreCannotEatTwoTokensDueToPopulation(BaseTestFeeding):
    """Carnivore can only eat as many tokens as its population."""

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        scavenger_carnivore = Species(
            food=4, body=1, population=5,
            traits=[Trait.carnivore, Trait.scavenger])
        cls.player1.boards = [scavenger_carnivore]
        cls.player2.boards = [scavenger_carnivore.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=6, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 5
        expected_players[1].boards[0].population = 4

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=5, deck=[])


class TestCooperativeCarnivoreAndScavengerButNotEnoughTokens(BaseTestFeeding):
    """Cooperation happens first, then Scavenger in order of given players.

    In this case, Scavenger shouldn't be triggered on player 2 since there
    aren't enough tokens on the WHB.
    """

    @classmethod
    def setup_class(cls):
        cls.feeding = CarnivoreFeeding(
            attacker_index=0, opponent_index=0, defender_index=0)
        super().setup_class()

        cooperative_carnivore = Species(
            food=1, body=1, population=7,
            traits=[Trait.carnivore, Trait.cooperation])
        scavenger = Species(
            food=3, body=1, population=6,
            traits=[Trait.scavenger, Trait.carnivore])

        cls.player1.boards = [cooperative_carnivore, scavenger]
        cls.player2.boards = [scavenger.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=3, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3
        ]
        expected_players[0].boards[0].food = 2
        expected_players[0].boards[1].food = 5
        expected_players[1].boards[0].population = 5

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestFertile(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        fertile_species = Species(
            food=0, body=1, population=1, traits=[Trait.fertile])

        cls.player1.boards = [fertile_species]
        cls.player2.boards = [fertile_species.copy()]
        cls.player3.boards = [fertile_species.copy(), fertile_species.copy()]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=0, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3.copy(),
        ]

        cls.before_dealer.handle_fertile()

        for player in expected_players:
            for species in player.boards:
                species.population += 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestFertilePopulationMax(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        fertile_species = Species(
            food=0, body=1, population=7, traits=[Trait.fertile])

        cls.player1.boards = [fertile_species]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=0, deck=[])
        cls.before_dealer.handle_fertile()
        cls.expected_dealer = cls.before_dealer


class TestLongNeck(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = NoFeeding()
        super().setup_class()

        long_neck_species = Species(
            food=0, body=1, population=1, traits=[Trait.long_neck])

        cls.player1.boards = [long_neck_species]
        cls.player2.boards = [
            long_neck_species.copy(),
            long_neck_species.copy()
        ]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=4)

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3,
        ]

        cls.before_dealer.handle_long_neck()

        expected_players[0].boards[0].food += 1
        expected_players[1].boards[0].food += 1
        expected_players[1].boards[1].food += 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=1, deck=[])


class TestLongNeckNotEnoughTokensAtWHB(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = NoFeeding()
        super().setup_class()

        long_neck_species = Species(
            food=0, body=1, population=1, traits=[Trait.long_neck])

        cls.player1.boards = [long_neck_species]
        cls.player2.boards = [
            long_neck_species.copy(),
            long_neck_species.copy()
        ]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=2)

        expected_players = [
            cls.player1.copy(),
            cls.player2.copy(),
            cls.player3,
        ]

        cls.before_dealer.handle_long_neck()

        expected_players[0].boards[0].food += 1
        expected_players[1].boards[0].food += 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestLongNeckTriggersForagingAndCooperation(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=1)
        super().setup_class()

        long_neck_foraging_and_cooperation_species = Species(
            food=1, body=3, population=3,
            traits=[Trait.cooperation, Trait.foraging, Trait.long_neck])
        empty_species = Species(
            food=0, body=1, population=3, traits=[])

        cls.player1.boards = [
            long_neck_foraging_and_cooperation_species,
            empty_species
        ]

        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=4, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3
        ]

        cls.before_dealer.handle_long_neck()

        after_player = expected_players[0]
        after_player.boards[0].food += 2
        after_player.boards[1].food += 2

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestFatTissueTransferReachesPopulationMax(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = NoFeeding()
        super().setup_class()

        fat_tissue_species = Species(
            food=0, body=3, population=1,
            fat_food=2, traits=[Trait.fat_tissue])

        cls.player1.boards = [fat_tissue_species]
        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=0, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3,
        ]

        cls.before_dealer.handle_fat_tissue_transfer()

        expected_players[0].boards[0].food += 1
        expected_players[0].boards[0].fat_food -= 1

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])


class TestFatTissueTransferOneToken(BaseTestFeeding):
    @classmethod
    def setup_class(cls):
        cls.feeding = VegetarianFeeding(species_index=0)
        super().setup_class()

        fat_tissue_species = Species(
            food=0, body=3, population=3,
            fat_food=2, traits=[Trait.fat_tissue])

        cls.player1.boards = [fat_tissue_species]
        players = [cls.player1, cls.player2, cls.player3]

        cls.before_dealer = Dealer(players=players, watering_hole=0, deck=[])

        expected_players = [
            cls.player1.copy(),
            cls.player2,
            cls.player3,
        ]

        cls.before_dealer.handle_fat_tissue_transfer()

        expected_players[0].boards[0].food += 2
        expected_players[0].boards[0].fat_food -= 2

        cls.expected_dealer = Dealer(
            players=expected_players, watering_hole=0, deck=[])
