from evolution.client.dealer_proxy import StaticDealerProxy
from evolution.server.exception import CheatingPlayerException
from evolution.server.player_proxy import StaticPlayerProxy


class MockPlayerProxy:
    def start(self, *args):
        pass

    def choose(self, player, before_opponents, after_opponents):
        pass

    def feedNext(self, player, watering_hole, opponents):
        pass


class MockCheatingPlayer:
    def can_feed(self, watering_hole, opponents):
        return True

    def play_cards(self, before_opponents, after_opponents):
        raise CheatingPlayerException

    def feedNext(self, watering_hole, opponents):
        raise CheatingPlayerException

    def end_game(self):
        pass


class MockCardPlayPlayer:
    def __eq__(self, other):
        return isinstance(other, MockCardPlayPlayer)

    def play_cards(self, before, after):
        return 3


class TestFestProxy(StaticPlayerProxy):
    def __init__(self, *args, **kwargs):
        self.action4 = None
        self.internal_player = None
        super().__init__(external=StaticDealerProxy())

    def choose(self, player, before_opponents, after_opponents):
        """request and validate external player card play actions

        :param player: state of player in the game
        :type player: Player

        :param before_opponents: opponents who played before the current player
        :type before_opponents: list of Player

        :param after_opponents: opponents who play after the current player
        :type after_opponents: list of Player

        :returns: (watering_hole_card_index, actions to execute)
        :rtype: (Natural, list of Action)
        """

        return self._deserialize_action4(self.action4, self.internal_player)

    def feedNext(self, player, watering_hole, opponents):
        """Asks external player and play cards and returns the feeding

        :param player: player
        :type player: Player

        :param watering_hole: number of tokens remaining at the watering hole
        :type watering_hole: Natural+

        :param opponents: all opponents of the player
        :type opponents: list of Player

        :returns: feeding chosen by external player
        :rtype: Feeding
        """

        state = [
            player.bag,
            [species.to_json() for species in player.boards],
            [card.to_json() for card in player.cards],
            watering_hole,
            self._serialize_boards(opponents)
        ]
        return self._deserialize_feeding(self.external.feedNext(state))


class MockProxyPlayerWithActions:

    def __init__(self, actions):
        self.actions = actions

    def choose(self, *args):
        whb_action, species_actions = self.actions
        return whb_action, species_actions


class MockProxyPlayerWithFeeding:

    def __init__(self, feeding):
        self.feeding = feeding

    def feedNext(self, *args):
        return self.feeding
