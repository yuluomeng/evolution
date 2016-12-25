import socket

from evolution.core.player import BasePlayer
from evolution.server.exception import CheatingPlayerException
from evolution.server.feeding import (
    CarnivoreFeeding, FatTissueFeeding, VegetarianFeeding, NoFeeding)
from evolution.server.species import Species
from evolution.core.trait import Trait
from evolution.core.utils import get_neighbors


class Player(BasePlayer):
    """
    :attr proxy: the external player to interact with
    :type: proxy: ProxyPlayer
    """

    def __init__(self, id, proxy, boards=None, bag=0, cards=None):
        self.proxy = proxy
        super().__init__(id, boards, bag, cards)

    def copy(self):
        """Creates a new instance of Player with the same attributes

        :returns: new instance of Player equal to the current instance
        :rtype: Player
        """

        return Player(
            self._id,
            self.proxy,
            [species.copy() for species in self.boards],
            self.bag,
            [card.copy() for card in self.cards])

    def start(self, watering_hole):
        """Informs the external player that the turn is about to start

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural
        """

        try:
            self.proxy.start(watering_hole, self)
        except (socket.error, TimeoutError):
            raise CheatingPlayerException

    def play_cards(self, before_opponents, after_opponents):
        """Executes external player card choices

        :param before_opponents: players who played before the current player
        :type before_player: list of Player

        :param after_opponents: players who play after the current player
        :type after_players: list of Player

        :returns: number of tokens to add the to watering hole
        :rtype: int

        :raises CheatingPlayerException
        """

        whb_discard_index, actions, cards_played = self._choose(
            before_opponents, after_opponents)

        watering_hole_tokens = self.cards[whb_discard_index].food

        for card_play in actions:
            try:
                card_play.apply(self)
            except ValueError:
                raise CheatingPlayerException

        current_cards = self.player_hand_indices()
        cards_remaining = current_cards - cards_played
        self.cards = [
            card for i, card in enumerate(self.cards)
            if i in cards_remaining
        ]

        return watering_hole_tokens

    def _choose(self, before_opponents, after_opponents):
        """grab and validate external player card play actions

        :param before_opponents: opponents who played before the current player
        :type before_opponents: list of Player

        :param after_opponents: opponents who play after the current player
        :type after_opponents: list of Player

        :returns: (watering_hole_card_index, actions to execute)
        :rtype: (Natural, list of Action)
        """
        try:
            whb_action, species_actions = self.proxy.choose(
                self, before_opponents, after_opponents)
        except (socket.error, TimeoutError, ValueError):
            raise CheatingPlayerException

        cards_played = self._cards_played_in_actions(
            [whb_action] + species_actions)
        return whb_action.card_index, species_actions, cards_played

    def _cards_played_in_actions(self, actions):
        """All cards played to execute the given actions

        Raises an value error if a card is used in more than one action.

        :param actions: the actions that the external
        :type actions: list of Actions

        :return: card indices representing all cards used to execute actions
        :rtype: set of Natural

        :raises: CheatingPlayerException if a card is used multiple times
        """

        ## set of indices representing cards in the player's hand
        cards_indices_played = set()
        for action in actions:
            cards_for_action = action.cards_used()
            if cards_for_action & cards_indices_played:
                raise CheatingPlayerException(
                    'cannot use a card more than once')

            player_hand = self.player_hand_indices()
            if cards_for_action - player_hand:
                raise CheatingPlayerException(
                    'must use a card in the player\'s hand')

            cards_indices_played |= cards_for_action
        return cards_indices_played

    def feedNext(self, watering_hole, opponents):
        """Chooses a feeding action to take.

        :param watering_hole: number of tokens remaining on the watering_hole
        :type watering_hole: Natural+

        :param opponents: the other players in the game
        :type opponents: list of player

        :returns: feeding player wishes to make
        :rtype: Feeding

        :raises: CheatingPlayerException
        """

        choices = self.get_feeding_choices(watering_hole, opponents)
        if len(choices) == 0:
            return NoFeeding()
        if len(choices) == 1:
            return choices.pop()

        try:
            choice = self.proxy.feedNext(self, watering_hole, opponents)
        except (socket.error, TimeoutError, ValueError):
            raise CheatingPlayerException

        choices.add(NoFeeding())
        if choice not in choices:
            raise CheatingPlayerException

        return choice

    def end_turn(self):
        """Handle the end turn actions"""

        self.try_reduce_population_to_food()
        self.move_food_to_bag()

    def end_game(self):
        """Notifies the external player that the game is over

        @todo: actually notify the external player

        :returns: the final score of the player
        :rtype: Natural+
        """

        self.proxy.end_game()
        return self.score()

    def score(self):
        """Calculates the current score of the given player

        :returns: the score of the player
        :rtype: Natural+
        """

        return self.bag + sum(species.score() for species in self.boards)

    def add_empty_species(self):
        """Add an empty species to self.boards"""

        self.boards.append(Species())

    def reduce_population(self, species_index):
        """Reduces the population of the given species

        :param species_index: index of the species in the player's boards
        :type species_index: Natural

        :returns: new population of the species
        :rtype: Nat
        """

        return self.boards[species_index].reduce_population()

    def get_feeding_choices(self, watering_hole, opponents):
        """All valid feeding choices for the player

        :param opponents: opponents that a carnivore might attack
        :type opponents: list of Player

        :returns: all valid feeding choices
        :rtype: set of Feeding
        """

        choices = set()

        if watering_hole == 0:
            return choices

        for species_index, species in enumerate(self.boards):
            if species.fat_food_need() > 0:
                choices |= {
                    FatTissueFeeding(species_index, tokens)
                    for tokens in range(1, species.fat_food_need() + 1)
                }

            if species.hunger() == 0:
                continue

            if Trait.carnivore in species.traits:
                choices |= {
                    CarnivoreFeeding(
                        species_index, opponent_index, defender_index)
                    for opponent_index, opponent in enumerate(opponents)
                    for defender_index in opponent.attackable_boards(species)
                }
            else:
                choices.add(VegetarianFeeding(species_index))

        return choices

    def player_hand_indices(self):
        """All indices that represent cards in a player's hand

        :returns: all indices represent cards in a player's hand
        :rtype: set of Natural
        """

        return set(range(len(self.cards)))

    def attackable_boards(self, attacker):
        """All boards that can be attacked by a given species

        :param attacker: attacking species
        :type attacker: Species

        :returns: indexes of all attackable species boards
        :rtype: list of Natural
        """

        attackable_boards = []
        for index, species in enumerate(self.boards):
            lneighbor, rneighbor = get_neighbors(self.boards, index)
            if species.is_attackable(attacker, lneighbor, rneighbor):
                attackable_boards.append(index)
        return attackable_boards

    def species_has_trait(self, species_index, trait):
        """Returns whether the species at the species_index has a given trait

        :param species_index: index of species to check
        :type species_index: Natural

        :param trait: trait to check for inclusion
        :type trait: Trait

        :returns: whether the species at the species_index has a given trait
        :rtype: bool
        """

        return trait in self.boards[species_index].traits

    def trigger_cooperation(self, species_index, dealer):
        """Applies cooperation if the species has the trait

        :param species_index: index of the species in the player's boards
        :type species_index: Natural

        :param dealer: keeper of the state of the game, which is mutated
        :type dealer: Dealer
        """

        _, rneighbor = get_neighbors(self.boards, species_index)

        if (self.species_has_trait(species_index, Trait.cooperation) and
                rneighbor):
            rneighbor_index = species_index + 1
            self.try_feed(rneighbor_index, dealer)

    def handle_scavenger(self, dealer):
        """Handles scavenger trait across all boards.

        :param dealer: keeper of the state of the game, which is mutated
        :type dealer: Dealer
        """
        for species_index, species in enumerate(self.boards):
            if Trait.scavenger in species.traits:
                self.try_feed(species_index, dealer)

    def handle_fertile(self):
        """Handles fertile trait across all boards"""

        for species in self.boards:
            if Trait.fertile in species.traits:
                species.try_reproduce()

    def handle_long_neck(self, dealer):
        """Handles long neck trait across all boards

        :param dealer: dealer of game
        :type dealer: Dealer
        """

        for species_index, species in enumerate(self.boards):
            if Trait.long_neck in species.traits:
                self.try_feed(species_index, dealer)

    def handle_fat_tissue_transfer(self):
        """Handles the fat tissue transfer from fat food to food"""

        for species in self.boards:
            if species.fat_food > 0:
                species.try_fat_tissue_transfer()

    def can_feed(self, watering_hole, opponents):
        """Can any of the player's species feed?

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural

        :param opponents: the other players in the game
        :type opponents: list of Player

        :returns: True if the player has boards that can eat, False otherwise
        :rtype: bool
        """
        feeding_options = self.get_feeding_choices(watering_hole, opponents)
        return True if feeding_options else False

    def try_feed(self, species_index, dealer):
        """Feeds the species at the species_index, if possible.

        :param species_index: index of the species in the player's boards
        :type species_index: Natural

        :param dealer: (mutable) keeper of the state of the game
        :type dealer: Dealer

        :returns: if the species was fed
        :rtype: bool
        """

        species = self.boards[species_index]
        tokens_fed = species.try_eat(dealer.watering_hole)
        if tokens_fed:
            dealer.watering_hole -= tokens_fed
            for feeding in range(tokens_fed):
                self.trigger_cooperation(species_index, dealer)
            return True
        return False

    def try_feed_fat_tissue(self, species_index, tokens, dealer):
        """Feeds the fat tissue of a species a passed number of tokens

        :param species_index: index of the species in the player's board
        :type species_index: Natural

        :param tokens: number of tokens to add to fat tissue
        :type tokens: Natural

        :param dealer: (mutable) keeper of the state of the game
        :type dealer: Dealer
        """

        species = self.boards[species_index]
        dealer.watering_hole -= species.try_take_fat_food(
            tokens, dealer.watering_hole)

    def try_reduce_population_to_food(self):
        """Reduce all boards' populations to their food token count."""

        for species in self.boards:
            species.try_reduce_population_to_food()

    def move_food_to_bag(self):
        """Move food from player boards to the bag"""

        self.bag += sum(species.reset_food() for species in self.boards)

    def remove_extinct(self):
        """Removes the extinct species from the player's boards

        :returns: number of extinct species removed
        :rtype: Natural
        """
        new_boards = [
            species for species in self.boards if species.population > 0
        ]
        count = len(self.boards) - len(new_boards)
        self.boards = new_boards
        return count

    def to_json(self):
        """Converts Player into JSON representation

        :returns: JSON representation of the current player state
        :rtype: JPlayer
        """

        return [
            self.bag,
            [species.to_json() for species in self.boards],
            [card.to_json() for card in self.cards]
        ]
