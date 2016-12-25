from itertools import product
from operator import itemgetter

from evolution.core.utils import split_at
from evolution.core.trait import Trait
from evolution.server.card import Card
from evolution.server.exception import CheatingPlayerException


class Dealer:
    """
    :attr players: all players in game, ordered by turn from left to right
    :type players: list of Player

    :attr watering_hole: number of tokens at the watering hole
    :type watering_hole: Natural

    :attr deck: cards yet to be played, ordered from top of deck to bottom
    :type bag: list of Card

    :attr current_feeding_index: index of the player whose turn it is to feed
    :type current_feeding_index: Natural
    """

    MIN_WATERING_HOLE = 0
    MAX_NON_CARNIVORE_CARDS, MAX_CARNIVORE_CARDS = 7, 17
    CARDS_PER_EXTINCTION = 2
    CARDS_PER_SPECIES = 1
    DEFAULT_CARDS_PER_PLAYER = 3

    def __init__(self, players, watering_hole=0, deck=None):
        self.players = players
        self.watering_hole = watering_hole
        self.deck = deck or []
        self.current_feeding_index = 0

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.players == other.players and
                self.watering_hole == other.watering_hole and
                self.deck == other.deck)

    def __repr__(self):
        return (
            '<Dealer> players: {self.players}, '
            'watering_hole: {self.watering_hole}, deck: {self.deck}'
            .format(self=self))

    def run_game(self):
        """Runs the simulation of Evolution"""

        self.deck = self._make_deck()

        while not self._is_game_over():
            self.start_turn()
            self.run_turn()
            self.end_turn()
            self._move_first_player_to_last()
        return self.final_scores()

    def start_turn(self):
        """Gives players species and cards at the beginning of the turn"""

        for player in self.players:
            if not player.boards:
                player.add_empty_species()
            self.give_cards(
                player,
                self.DEFAULT_CARDS_PER_PLAYER + len(player.boards))

            player.start(self.watering_hole)

    def run_turn(self):
        """Runs the fourth step of Evolution"""

        self.handle_play_cards()
        self.handle_fertile()
        self.handle_long_neck()
        self.handle_fat_tissue_transfer()
        self.handle_feeding()

    def end_turn(self):
        """Handle end of turn actions"""

        for player in self.players:
            player.end_turn()
            self.remove_extinct(player)

    def final_scores(self):
        """The final scores of the game.

        :returns: mapping of player_id -> score in descending order of scores
        :rtype: list of (Natural, Natural+)
        """
        return sorted(
            ((player._id, player.end_game()) for player in self.players),
            key=itemgetter(1),
            reverse=True)

    def handle_play_cards(self):
        """Tells player to play cards to add food to watering hole."""

        cheating_players = []

        for i, player in enumerate(self.players):
            before, after = split_at(self.players, i, exclusive=True)
            try:

                self.watering_hole += player.play_cards(before, after)
            except CheatingPlayerException:
                cheating_players.append(player)
            self.watering_hole = max(
                self.watering_hole, self.MIN_WATERING_HOLE)

        for player in cheating_players:
            self.handle_cheating_player(player)

    def handle_feeding(self):
        """Runs the feeding step in the game"""

        while self.watering_hole > 0 and self.boards_still_hungry():
            try:
                self.feed1()
            except CheatingPlayerException:
                cheater = self.players[self.current_feeding_index]
                self.handle_cheating_player(cheater)
            else:
                self._increment_feeding_index()

    def feed1(self):
        """Executes one step in the feeding cycle"""

        player = self.players[self.current_feeding_index]
        opponents = self._current_opponents()
        feeding = player.feedNext(self.watering_hole, opponents)
        feeding.execute(self, player, opponents)

    def remove_extinct(self, player):
        """Remove all extinct species from the player"""

        num_extinct_boards = player.remove_extinct()
        self.give_cards(player, num_extinct_boards * self.CARDS_PER_EXTINCTION)

    def give_cards(self, player, num_cards):
        """Gives cards to the given player

        :param player: player to add cards to
        :type player: Player

        :param num_cards: number of cards to add
        :type num_cards: Natural+
        """

        player_cards, self.deck = split_at(self.deck, num_cards)
        player.cards.extend(player_cards)

    def trigger_scavenger(self):
        """Handles the scavenger trait after each attack"""

        for player in self._feeding_order():
            player.handle_scavenger(self)

    def handle_fertile(self):
        """Tells players to handle fertile boards"""

        for player in self.players:
            player.handle_fertile()

    def handle_long_neck(self):
        """Tells players to handle boards with long neck"""

        for player in self.players:
            player.handle_long_neck(self)

    def handle_fat_tissue_transfer(self):
        """Tells players to handle fat tissue transfer"""

        for player in self.players:
            player.handle_fat_tissue_transfer()

    def handle_cheating_player(self, player):
        """Removes a cheating player from the game

        :param player: cheating player to remove from game
        :type player: Player
        """
        player.end_game()
        self.players.remove(player)

    def boards_still_hungry(self):
        """Are there still hungry species in the game?

        :returns: True if there are hungry species, False otherwise
        :rtype: bool
        """

        return any(
            player.can_feed(
                self.watering_hole,
                self._current_opponents(player_index))
            for player_index, player in enumerate(self.players))

    @staticmethod
    def _make_deck():
        """Makes a starting deck for Evolution

        :returns: deck of cards ordered from smallest to largest
        :rtype: list of Card
        """

        carnivore_cards = [
            Card(food, Trait.carnivore)
            for food in range(
                Card.MIN_CARNIVORE_FOOD, Card.MAX_CARNIVORE_FOOD+1)
        ]

        food_trait_combinations = product(
            range(Card.MIN_NON_CARNIVORE_FOOD, Card.MAX_NON_CARNIVORE_FOOD+1),
            Trait)
        non_carnivore_cards = [
            Card(food, trait)
            for food, trait in food_trait_combinations
            if trait is not Trait.carnivore
        ]

        return list(sorted(carnivore_cards + non_carnivore_cards))

    def _increment_feeding_index(self):
        """Change the current feeding index to the next player in the game

        Effect: Modifies self.current_feeding_index
        """

        self.current_feeding_index = (
            (self.current_feeding_index + 1) % len(self.players))

    def _move_first_player_to_last(self):
        """Move the first player in self.players to the end

        Effect: Changes the order of players in self.players
        """

        if self.players:
            self.players.append(self.players.pop(0))

    def _current_opponents(self, player_index=None):
        """All players other than the current player

        :rtype: list of Player
        """
        current_feeding_index = player_index or self.current_feeding_index

        return [
            player for i, player in enumerate(self.players)
            if i != current_feeding_index
        ]

    def _feeding_order(self):
        """All players, starting at staring_player and wrapping around

        :returns: newly ordered list of players
        :rtype: list of Player
        """

        return (
            self.players[self.current_feeding_index:] +
            self.players[:self.current_feeding_index])

    def _is_game_over(self):
        """Is the current game over?

        :returns: whether the current game is over
        :rtype: bool
        """

        num_cards_needed = sum(
            self.DEFAULT_CARDS_PER_PLAYER + len(player.boards)
            for player in self.players)

        return len(self.deck) < num_cards_needed or not self.players
