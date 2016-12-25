from evolution.core.trait import Trait
from evolution.core.species import BaseSpecies


class Species(BaseSpecies):

    MIN_BODY, MAX_BODY = 0, 7
    MIN_POPULATION, MAX_POPULATION = 1, 7

    def score(self):
        """Score contributed by this species

        :returns: population size + number of traits
        :rtype: Natural+
        """

        return self.population + len(self.traits)

    def replace_trait(self, trait_index, new_trait):
        """Replace the trait at the given trait_index with the new trait

        :param trait_index: index of trait to replace
        :type trait_index: Natural

        :param trait: new trait for species
        :type trait: Trait
        """

        old_trait = self.traits[trait_index]
        if old_trait is Trait.fat_tissue and new_trait is not Trait.fat_tissue:
            self.fat_food = 0

        self.traits[trait_index] = new_trait

    def food_bag_transfer(self):
        """Moves food to the bag

        :returns: number of tokens to add to the player's bag
        :rtype: Nat
        """

        add_food = self.food
        self.food = 0
        return add_food

    def reduce_population(self):
        """Reduce the population by 1

        This may also decrease the species' food

        :return: new population
        :rtype: Nat
        """

        self.population -= 1
        self.food = min(self.food, self.population)
        return self.population

    def try_eat(self, watering_hole):
        """Eat, if possible.

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural+

        :returns: number of tokens eaten
        :rtype: Natural
        """

        default_tokens = 2 if Trait.foraging in self.traits else 1
        tokens_to_eat = min(default_tokens, watering_hole, self.hunger())

        self.food += tokens_to_eat
        return tokens_to_eat

    def try_reproduce(self):
        """Tries to add population the species if it's under the max"""

        self.population = min(self.MAX_POPULATION, self.population + 1)

    def try_add_body(self):
        """Tries to add body the species if it's under the max"""

        self.body = min(self.MAX_BODY, self.body + 1)

    def try_take_fat_food(self, tokens, watering_hole):
        """Take fat food, if possible.

        :param tokens: number of tokens to try to add to fat tissue
        :type tokens: Natural

        :param watering_hole: number of tokens at the watering hole
        :type watering_hole: Natural+

        :returns: number of tokens added to fat_food
        :rtype: Natural
        """
        assert Trait.fat_tissue in self.traits

        tokens_to_take = min(watering_hole, tokens)
        self.fat_food += tokens_to_take
        return tokens_to_take

    def reset_food(self):
        """Sets food to 0 and returns the original value

        :returns: number of food tokens removed
        :rtype: Nat
        """

        add_food = self.food
        self.food = 0
        return add_food

    def try_fat_tissue_transfer(self):
        """Tries to move fat food to food"""

        tokens_to_transfer = min(self.hunger(), self.fat_food)
        self.food += tokens_to_transfer
        self.fat_food -= tokens_to_transfer

    def try_reduce_population_to_food(self):
        """Set population to food value if population is higher"""

        self.population = min(self.population, self.food)
