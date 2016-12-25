"""
A JCard is [FoodValue, JTrait].
    - A FoodValue is a JSON number interpretable as an integer in [-8, 8].
    - It must match one of the game cards allowed according to the
      specifications of Evolution.
"""


class BaseCard:
    """
    :attr food: number of food tokens associated with the card
    :type food: int

    :attr trait: trait associated with the card
    :type trait: Trait
    """

    def __init__(self, food, trait):
        self.food = food
        self.trait = trait

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.food == other.food and
            self.trait == other.trait)

    def __lt__(self, other):
        return (self.trait, self.food) < (other.trait, other.food)

    def __repr__(self):
        return ('<Card> food: {self.food}, trait: {self.trait}'
                .format(self=self))

    def to_json(self):
        """Converts a Card to its JSON representation

        :returns: JSON representation of the current card
        :rtype: JCard
        """

        return [self.food, self.trait.to_json()]
