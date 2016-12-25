from evolution.core.card import BaseCard


class Card(BaseCard):

    MIN_CARNIVORE_FOOD, MAX_CARNIVORE_FOOD = -8, 8
    MIN_NON_CARNIVORE_FOOD, MAX_NON_CARNIVORE_FOOD = -3, 3

    def copy(self):
        return self.__class__(self.food, self.trait)
