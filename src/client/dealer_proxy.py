from enum import Enum
import socket

from evolution.core.connection import send_msg, read_msg
from evolution.core.utils import (
    assert_list_with_size, is_natural, is_natural_plus, lmap)
from evolution.client import strategy
from evolution.client.action import (
    AddToWateringHole, AddPopulation, AddBody, AddSpecies, ReplaceTrait)
from evolution.client.data import Card, Opponent, Player, Species


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

CHOOSE_MSG_LEN = 2
START_MSG_LEN = 4
FEED_NEXT_MSG_LEN = 5


class TurnEnum(Enum):

    def is_valid_transition(self, next_turn):
        """Is the next turn a valid transition from the current turn?

        :param current_turn: the current turn of the game
        :type current_turn: Turn

        :param next_turn: the proposed next turn of the game
        :type next_turn: Turn

        :returns: whether the next turn is a valid transition
        :rtype: bool
        """

        if self is Turn.unstarted:
            return next_turn in {Turn.unstarted, Turn.start}
        if self is Turn.start:
            return next_turn is Turn.choose
        if self is Turn.choose:
            return next_turn in {Turn.start, Turn.feedNext}
        if self is Turn.feedNext:
            return next_turn in {Turn.start, Turn.feedNext}

    @classmethod
    def from_msg(cls, msg):
        """The turn tha tthe given message represents

        :param msg: the JSON msg that represents a turn
        :type msg: JSON

        :returns: Turn the message represents
        :rtype: Turn

        :raises: ValueError if the msg does not represent a turn
        """

        if msg == RemoteDealerProxy.SIGN_UP_RESPONSE:
            return cls.unstarted

        if not isinstance(msg, list):
            raise ValueError('All messages from dealer must be a list')

        if len(msg) == CHOOSE_MSG_LEN:
            return cls.choose
        if len(msg) == START_MSG_LEN:
            return cls.start
        if len(msg) == FEED_NEXT_MSG_LEN:
            return cls.feedNext

        raise ValueError('Invalid message length from dealer')


Turn = TurnEnum('Turn', ['unstarted', 'start', 'choose', 'feedNext'])


class BaseDealerProxy:

    def __init__(self):
        """
        :attr current_turn: the current turn of the game
        :type current_turn: Turn

        :attr player_state: the current state of the player
        :type player_state: Player
        """

        self.current_turn = Turn.unstarted
        self.player_state = Player()

    def _set_player_state(self, watering_hole, jplayer):
        """Updates the player's knowledge of the state of the game

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural

        :param jplayer: current state of the player
        :type jplayer: JPlayer

        :effect: updates the value of self.player_state
        """

        if not is_natural(watering_hole):
            raise ValueError('Watering hole must be a Natural')

        self.player_state = Player.from_json(jplayer)

    def _choose_actions(self, before_jopponents, after_jopponents):
        """Choose actions to play

        :param before_jopponents: opponents who play before the current player
        :type before_jopponents: list of JOpponent

        :param after_jopponents: opponents who play after the current player
        :type after_jopponents: list of JOpponent

        :returns: actions to play
        :rtype: list of Action
        """

        if not (isinstance(before_jopponents, list) and
                isinstance(after_jopponents, list)):
            raise ValueError('Before and after opponents must be lists')

        before_opponents = lmap(Opponent.from_json, before_jopponents)
        after_opponents = lmap(Opponent.from_json, after_jopponents)
        return strategy.play_cards(
            self.player_state, before_opponents, after_opponents)

    def _choose_feeding(self, bag, jboards, jcards, watering_hole, jopponents):
        """Choose a feeding to make

        :param bag: number of tokens in the player's food bag
        :type bag: Natural

        :param jboards: boards that the player owns
        :type jboards: list of JSpecies

        :param jcards: cards in the player's hand
        :type jcards: list of JCard

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural+

        :param jopponents: boards owned by the player's opponents
        :type jopponents: list of JOpponent

        :returns: feeding choice made by player
        :rtype: Feeding
        """

        if not is_natural(bag):
            raise ValueError('Player\'s bag must be a Natural')

        if not (isinstance(jboards, list) and
                isinstance(jcards, list) and
                isinstance(jopponents, list)):
            raise ValueError('jboards, jcards, jopponents must all be lists')

        if not is_natural_plus(watering_hole):
            raise ValueError('Watering hole must be a natural plus')

        boards = lmap(Species.from_json, jboards)
        cards = lmap(Card.from_json, jcards)
        opponents = lmap(Opponent.from_json, jopponents)

        player = Player(bag=bag, boards=boards, cards=cards)

        return strategy.feedNext(player, watering_hole, opponents)

    @staticmethod
    def _serialize_actions(actions):
        """
        :param actions: actions a player wishes to make
        :type actions: dict of (Action -> Action or list of Action)

        :returns: serialized actions for the dealer
        :rtype: JAction4
        """

        jaction4 = [actions[AddToWateringHole].to_json()]
        for action_type in [AddPopulation, AddBody, AddSpecies, ReplaceTrait]:
            jaction4.append(
                [action.to_json() for action in actions.get(action_type, [])])

        return jaction4

    def _validate_next_turn(self, next_turn):
        """Makes sure the turn transition is valid according to the protocol

        :param next_turn: the new turn the dealer has moved to
        :type next_turn: Turn

        :raises: ValueError if the turn transition is invalid
        """

        if not self.current_turn.is_valid_transition(next_turn):
            raise ValueError(
                '{} -> {} is invalid transition'.format(
                    self.current_turn, next_turn))


class RemoteDealerProxy(BaseDealerProxy):

    SIGN_UP_MSG = 'hello'
    SIGN_UP_RESPONSE = 'ok'

    def __init__(self, host, port):
        """
        :attr sock: connection to the Dealer
        :type sock: socket.socket
        """

        self.sock = socket.create_connection((host, port))
        super().__init__()

    def request_join(self):
        """Send request to the server asking to join the game"""

        send_msg(self.SIGN_UP_MSG, self.sock)
        self._handle_msg()

    def _handle_msg(self):
        """Delegates the received message to the correct handler"""

        msg = read_msg(self.sock)
        if not msg:
            return

        next_turn = Turn.from_msg(msg)
        self._validate_next_turn(next_turn)

        self.current_turn = next_turn
        if self.current_turn is Turn.unstarted:
            self._handle_unstarted(msg)
        if self.current_turn is Turn.start:
            self._handle_start(msg)
        if self.current_turn is Turn.choose:
            self._handle_choose(msg)
        if self.current_turn is Turn.feedNext:
            self._handle_feedNext(msg)

        self._handle_msg()

    def _handle_unstarted(self, msg):
        """Handle response from the dealer of an unstarted game

        :raises: ValueError if the dealer does not respond positively
        """

        if msg != self.SIGN_UP_RESPONSE:
            raise ValueError('invalid registration response')

    def _handle_start(self, msg):
        """Lets the external player know that a new turn has started

        :param msg: message to signify start turn
        :type msg: [Natural, JPlayer]

        :effect: updates self.player_state
        """

        watering_hole, *jplayer = msg
        self._set_player_state(watering_hole, jplayer)

    def _handle_choose(self, msg):
        """Send the player's card plays across the socket

        :param msg: dealer message to deserialize into internal representations
        :type msg: [list of JOpponent, list of JOpponent]
        """

        actions = self._choose_actions(*msg)
        send_msg(self._serialize_actions(actions), self.sock)

    def _handle_feedNext(self, msg):
        """Send the player's feeding choice across the wire

        :param msg: dealer message to deserialize into internal representations
        :type msg: JState
        """

        feeding = self._choose_feeding(*msg)
        send_msg(feeding.to_json(), self.sock)


class StaticDealerProxy(BaseDealerProxy):

    def start(self, watering_hole, jplayer):
        """Update the state of the game for a new turn

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural

        :param jplayer: current state of the player
        :type jplayer: JPlayer

        :effect: updates the value of self.player_state
        """

        self._validate_next_turn(Turn.start)
        self.current_turn = Turn.start

        self._set_player_state(watering_hole, jplayer)

    def choose(self, before_jopponents, after_jopponents):
        """Pick the actions the player strategy would like to play

        :param before_jopponents: Opponents that picked before the player
        :type before_jopponents: list of Opponent

        :param after_jopponents: Opponents that picked after the player
        :type after_jopponents: list of Opponent

        :returns: the card plays the player would like to make
        :rtype: JAction4
        """

        self._validate_next_turn(Turn.choose)
        self.current_turn = Turn.choose

        actions = self._choose_actions(before_jopponents, after_jopponents)
        return self._serialize_actions(actions)

    def feedNext(self, state):
        """Pick a feeding choice

        :param state: the current state of the game
        :type state: State

        :returns: feeding choice to make
        :rtype: JFeeding
        """

        self._validate_next_turn(Turn.feedNext)
        self.current_turn = Turn.feedNext

        assert_list_with_size(state, FEED_NEXT_MSG_LEN)

        feeding = self._choose_feeding(*state)
        return feeding.to_json()
