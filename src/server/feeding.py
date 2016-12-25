from collections import namedtuple

from evolution.core.trait import Trait


class Feeding:

    def execute(self, dealer):
        """takes a dealer and handles the feeding

        :param dealer: dealer to modify based on feeding
        :type dealer: Dealer
        """

        raise NotImplementedError


class FatTissueFeeding(
        namedtuple('FatTissueFeeding', ['species_index', 'tokens']),
        Feeding):
    """
    :attr species_index: index of species to feed
    :type species_index: Natural

    :attr tokens: number of tokens requested
    :type tokens: int
    """

    def execute(self, dealer, player, opponents):
        species_index, tokens = self
        player.try_feed_fat_tissue(species_index, tokens, dealer)


class VegetarianFeeding(
        namedtuple('VegetarianFeeding', ['species_index']), Feeding):
    """
    :attr species_index: index of species to feed
    :type species_index: Natural
    """

    def execute(self, dealer, player, opponents):
        player.try_feed(self.species_index, dealer)


class CarnivoreFeeding(
        namedtuple(
            'CarnivoreFeeding',
            ['attacker_index', 'opponent_index', 'defender_index']),
        Feeding):
    """
    :attr attacker_index: index of attacking species
    :type attacker_index: Natural

    :attr opponent_index: index of player that is attacked
    :type opponent_index: Natural

    :attr defender_index: index of defending species
    :type defender_index: Natural
    """

    def execute(self, dealer, player, opponents):
        attacker_index, opponent_index, defender_index = self
        opponent = opponents[opponent_index]

        def reduce_population(player, species_index):
            new_population = player.reduce_population(species_index)
            dealer.remove_extinct(player)
            return new_population

        has_horns = opponent.species_has_trait(defender_index, Trait.horns)
        reduce_population(opponent, defender_index)
        if has_horns:
            if reduce_population(player, attacker_index) == 0:
                return

        if player.try_feed(attacker_index, dealer):
            dealer.trigger_scavenger()


class NoFeeding(namedtuple('NoFeeding', []), Feeding):

    def execute(self, dealer, player, opponents):
        pass
