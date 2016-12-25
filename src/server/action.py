from collections import namedtuple

from evolution.core.utils import assert_list_with_size, is_natural, lmap
from evolution.server.species import Species


class Action:

    @classmethod
    def from_json(cls, action, player):
        """converts the JSON action into our internal data representation

        :param action: action to convert
        :type action: JAction

        :param player: player the action is applied on
        :type player: Player

        :returns: internal representation of an Action
        :rtype: Action
        """
        raise NotImplementedError

    def _validate_action(self, player):
        """make sure the action is valid given the state of the player

        :param player: the intended target of the action
        :type player: Player

        raises a ValueError if the action is invalid
        """
        raise NotImplementedError

    def apply(self, player):
        """executes the action on the given player by mutating its state

        :param player: the intended target of the action
        :type player: Player
        """
        raise NotImplementedError

    def cards_used(self):
        """the cards indices that should be discarded after playing this action

        :returns: card indices that should be discarded
        :rtype: set of Natural
        """
        return {self.card_index}


class AddToWateringHole(
        namedtuple('AddToWateringHole', ['card_index']), Action):

    @classmethod
    def from_json(cls, whb_card_index):
        if not is_natural(whb_card_index):
            raise ValueError(
                'watering hole card index must be a natural')

        return cls(whb_card_index)


class ReplaceTrait(
        namedtuple(
            'ReplaceTrait', ['species_index', 'trait_index', 'card_index']),
        Action):

    RT_LEN = 3

    @classmethod
    def from_json(cls, rt):
        assert_list_with_size(rt, cls.RT_LEN, 'rt')

        if not all(is_natural(i) for i in rt):
            raise ValueError(
                'all indices in replace trait must be naturals')

        return cls(*rt)

    def _validate_action(self, player):
        if self.species_index >= len(player.boards):
            raise ValueError(
                'species_index must represent a species on player')
        if self.trait_index >= len(player.boards[self.species_index].traits):
            raise ValueError(
                'trait_index must represent a trait on the species')

    def apply(self, player):
        self._validate_action(player)
        species = player.boards[self.species_index]
        trait = player.cards[self.card_index].trait
        species.replace_trait(self.trait_index, trait)


class AddSpecies(
        namedtuple('AddSpecies', ['card_index', 'trait_card_indices']),
        Action):

    POSSIBLE_BT_LENS = [1, 4]

    @classmethod
    def from_json(cls, bt):
        assert_list_with_size(bt, cls.POSSIBLE_BT_LENS, 'bt')

        card_index, *trait_card_indices = bt

        all_card_indices = list(trait_card_indices) + [card_index]
        if not all(is_natural(i) for i in all_card_indices):
            raise ValueError(
                'All indices in AddSpecies must be Naturals')
        if len(set(all_card_indices)) != len(all_card_indices):
            raise ValueError(
                'No duplicate indices allowed in AddSpecies')

        return cls(card_index, trait_card_indices)

    def apply(self, player):
        traits = lmap(lambda i: player.cards[i].trait, self.trait_card_indices)
        new_species = Species(food=0, body=0, population=1, traits=traits)
        player.boards.append(new_species)

    def cards_used(self):
        return set(self.trait_card_indices) | {self.card_index}


class AddPopulation(
        namedtuple('AddPopulation', ['species_index', 'card_index']), Action):

    GP_LEN = 3

    @classmethod
    def from_json(cls, gp):
        assert_list_with_size(gp, cls.GP_LEN, 'gp')

        name, species_index, card_index = gp

        if name != 'population':
            raise ValueError('name of action must be "population"')
        if not (is_natural(species_index) and is_natural(card_index)):
            raise ValueError(
                'species_index and card_index must be Naturals')

        return cls(species_index, card_index)

    def _validate_action(self, player):
        if self.species_index >= len(player.boards):
            raise ValueError(
                'species_index must represent a valid species in boards')

    def apply(self, player):
        player.boards[self.species_index].try_reproduce()


class AddBody(namedtuple('AddBody', ['species_index', 'card_index']), Action):

    GB_LEN = 3

    @classmethod
    def from_json(cls, gb):
        assert_list_with_size(gb, cls.GB_LEN, 'gb')

        name, species_index, card_index = gb
        if name != 'body':
            raise ValueError('name of action must be "body"')
        if not (is_natural(species_index) and is_natural(card_index)):
            raise ValueError(
                'species_index and card_index must be Naturals')

        return cls(species_index, card_index)

    def _validate_action(self, player):
        if self.species_index >= len(player.boards):
            raise ValueError(
                'species_index must represent a valid species in boards')

    def apply(self, player):
        self._validate_action(player)
        player.boards[self.species_index].try_add_body()
