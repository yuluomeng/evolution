import socket

from evolution.core.connection import send_msg, read_msg
from evolution.server.action import (
    AddToWateringHole, AddSpecies, AddPopulation, ReplaceTrait, AddBody)
from evolution.server.feeding import (
    VegetarianFeeding, NoFeeding, CarnivoreFeeding, FatTissueFeeding)
from evolution.core.utils import assert_list_with_size, timeout


TIMEOUT_SECONDS = 2  # seconds to wait for external player to respond

"""
A JState is a
    [Natural, list of JSpecies, list of JCard, Natural+, list of Boards]

A JState represents all knowledge that a player can have of the game.
In order from left to right, the values of JState represent:
    - Tokens in the player's bag
    - The player's species boards
    - Cards in the player's hand
    - Number of tokens at the watering hole
    - The boards of opposing players
"""


class BasePlayerProxy:
    ACTION4_LEN = 5
    FAT_TISSUE_FEEDING_LEN = 2
    CARNIVORE_FEEDING_LEN = 3

    def start(self, watering_hole, player):
        """Informs the external player that the turn is about to start

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural

        :param player: the state of the player
        :type player: Player
        """

        raise NotImplementedError

    def choose(self, player, before_opponents, after_opponents):
        """Request card plays from external player

        :param player: state of player in the game
        :type player: Player

        :param before_opponents: opponents who played before the current player
        :type before_opponents: list of Player

        :param after_opponents: opponents who play after the current player
        :type after_opponents: list of Player

        :returns: (watering_hole_card_index, actions to execute)
        :rtype: (Natural, list of Action)
        """

        raise NotImplementedError

    def feedNext(self, player, watering_hole, opponents):
        """Request feeding choice from external player

        :param player: player
        :type player: Player

        :param watering_hole: number of tokens remaining at the watering hole
        :type watering_hole: Natural+

        :param opponents: all opponents of the player
        :type opponents: list of Opponent

        :returns: feeding chosen by external player
        :rtype: Feeding
        """

        raise NotImplementedError

    def end_game(self):
        """Lets the external player know the game is over"""

        raise NotImplementedError

    @staticmethod
    def _deserialize_action4(action4):
        """Converts the action4 to an internal representation of actions

        :param action4: JSON representation of actions a player wishes to make
        :type action4: Action4

        :param player: current state of the player
        :type player: Player

        :returns: (watering hole action, species actions)
        :rtype: AddToWateringHole, list of list of Action

        :raises: CheatingPlayerException if the actions are invalid.
        """
        assert_list_with_size(action4, BasePlayerProxy.ACTION4_LEN)

        [
            watering_hole_card_index, add_populations, add_bodies, add_boards,
            replace_traits
        ] = action4

        whb_action = AddToWateringHole.from_json(watering_hole_card_index)

        species_actions = (
            [AddSpecies.from_json(bt) for bt in add_boards] +
            [ReplaceTrait.from_json(rt) for rt in replace_traits] +
            [AddPopulation.from_json(gp) for gp in add_populations] +
            [AddBody.from_json(gb) for gb in add_bodies]
        )

        return whb_action, species_actions

    @classmethod
    def _deserialize_feeding(cls, jfeeding):
        """Converts the jfeeding to an internal representation of a feeding

        :param jfeeding: the JSON representation of a feeding
        :type jfeeding: JFeeding

        :returns: the internal representation of a feeding
        :rtype: Feeding

        :raises: ValueError if the feeding does not match the JSON spec
        """

        if jfeeding is False:
            return NoFeeding()
        if type(jfeeding) is int:
            return VegetarianFeeding(jfeeding)

        if isinstance(jfeeding, list):
            if len(jfeeding) == cls.FAT_TISSUE_FEEDING_LEN:
                return FatTissueFeeding(*jfeeding)
            if len(jfeeding) == cls.CARNIVORE_FEEDING_LEN:
                return CarnivoreFeeding(*jfeeding)

        raise ValueError('Invalid feeding response')

    @staticmethod
    def _serialize_boards(players):
        """Converts the players' boards into JSON

        :returns: JSON Species for each player
        :rtype: list of list of JSpecies
        """

        return [
            [species.to_json() for species in player.boards]
            for player in players
        ]

    @classmethod
    def _serialize_state(cls, player, watering_hole, opponents):
        """Creates a JSON representation of the state of the game

        :param player: player
        :type player: Player

        :param watering_hole: number of tokens remaining at the watering hole
        :type watering_hole: Natural+

        :param opponents: all opponents of the player
        :type opponents: list of Opponent

        :returns: JSON representation of the state of the game
        :rtype: JState
        """

        return [
            player.bag,
            [species.to_json() for species in player.boards],
            [card.to_json() for card in player.cards],
            watering_hole,
            cls._serialize_boards(opponents)
        ]


class RemotePlayerProxy(BasePlayerProxy):
    """Serialize / deserialize messages from a remotely linked player"""

    def __init__(self, sock):
        """
        :attr sock: connection to the external player
        :type sock: socket.socket
        """
        self.sock = sock

    def start(self, watering_hole, player):
        msg = [watering_hole] + player.to_json()
        send_msg(msg, self.sock)

    @timeout(TIMEOUT_SECONDS)
    def choose(self, player, before_opponents, after_opponents):
        opponents_boards = [
            self._serialize_boards(before_opponents),
            self._serialize_boards(after_opponents)
        ]

        send_msg(opponents_boards, self.sock)
        return self._deserialize_action4(read_msg(self.sock))

    @timeout(TIMEOUT_SECONDS)
    def feedNext(self, player, watering_hole, opponents):
        state = self._serialize_state(player, watering_hole, opponents)

        send_msg(state, self.sock)
        return self._deserialize_feeding(read_msg(self.sock))

    def end_game(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except socket.error:
            pass


class StaticPlayerProxy(BasePlayerProxy):
    """Serialize / deseriailze messages from a statically linked player"""

    def __init__(self, external):
        """
        :attr external: link to the external player
        :type external: StaticDealerProxy
        """
        self.external = external

    @timeout(TIMEOUT_SECONDS)
    def start(self, watering_hole, player):
        self.external.start(watering_hole, player.to_json())

    @timeout(TIMEOUT_SECONDS)
    def choose(self, player, before_opponents, after_opponents):
        before_jopponents = self._serialize_boards(before_opponents)
        after_jopponents = self._serialize_boards(after_opponents)

        requested_actions = self.external.choose(
            before_jopponents, after_jopponents)
        return self._deserialize_action4(requested_actions)

    @timeout(TIMEOUT_SECONDS)
    def feedNext(self, player, watering_hole, opponents):
        state = self._serialize_state(player, watering_hole, opponents)

        feeding_choice = self.external.feedNext(state)
        return self._deserialize_feeding(feeding_choice)

    def end_game(self):
        # nothing to do when ending the game for statically linked players
        pass
