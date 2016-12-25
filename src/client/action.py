from collections import namedtuple


"""
A JAction4 is a [Natural, [GP, ...], [GB, ...], [BT, ...], [RT, ...]]

Interpretation:
    - Every natural number in an Action4 represent an index into a
    sequence of species boards or cards.
    - The first natural number specifies the card that a player is turning into
    food.

Constraints:
    - The embedded arrays (GP, GB, BT, and RT) may be empty.


A JAction is one of:
    - Natural
    - GP
    - GB
    - BT
    - RT


A GP is a ["population", Natural, Natural].

Interpretation:
    - A ["population",i,j] array requests a trade of card j for a
    growth of the population of species board i by one.


A GB is a ["body", Natural, Natural].

Interpretation:
    - A ["body", i, j] array requests a trade of card j for a growth of
    the body of species board i by one.


A BT is one of:
    - [Natural]
    - [Natural, Natural]
    - [Natural, Natural, Natural]
    - [Natural, Natural, Natural, Natural]

Interpretation:
    - A BT represents a species board addition to the right of the
    existing sequence of boards for the corresponding player.
    - [i, j,..., k] uses the first of the player’s cards (i) to "pay" for the
    new board and uses the remaining (up to three) cards (j, ..., k) as traits.

Constraint:
    - Once a player has added a species board, it becomes impossible to add
    a trait.


An RT is a [Natural, Natural, Natural].

Interpretation:
    - An RT represents a trait replacement for a species board.
    - Specifically, [b, i, j] specifies that board b’s i’s trait card is
    replaced with the j’s card from the player’s card sequence.
"""


class Action:

    def to_json(self):
        """JSON representation of the action

        :returns: JSON representation
        :rtype: JAction
        """

        raise NotImplementedError


class AddToWateringHole(
        namedtuple('AddToWateringHole', ['card_index']), Action):

    def to_json(self):
        return self.card_index


class ReplaceTrait(
        namedtuple(
            'ReplaceTrait', ['species_index', 'trait_index', 'card_index']),
        Action):

    def to_json(self):
        return [self.species_index, self.trait_index, self.card_index]


class AddSpecies(
        namedtuple('AddSpecies', ['card_index', 'trait_card_indices']),
        Action):

    def to_json(self):
        return [self.card_index] + self.trait_card_indices


class AddPopulation(
        namedtuple('AddPopulation', ['species_index', 'card_index']), Action):

    def to_json(self):
        return ['population', self.species_index, self.card_index]


class AddBody(namedtuple('AddBody', ['species_index', 'card_index']), Action):

    def to_json(self):
        return ['body', self.species_index, self.card_index]
