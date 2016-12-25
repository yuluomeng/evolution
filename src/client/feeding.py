from collections import namedtuple


class Feeding:

    def to_json(self):
        """Returns JSON version of a Feeding

        :returns: JSON feeding
        :rtype: JFeeding
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

    def to_json(self):
        return [self.species_index, self.tokens]


class VegetarianFeeding(
        namedtuple('VegetarianFeeding', ['species_index']), Feeding):
    """
    :attr species_index: index of species to feed
    :type species_index: Natural
    """

    def to_json(self):
        return self.species_index


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

    def to_json(self):
        return [self.attacker_index, self.opponent_index, self.defender_index]


class NoFeeding(namedtuple('NoFeeding', []), Feeding):

    def to_json(self):
        return False
