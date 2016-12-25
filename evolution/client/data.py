from collections import namedtuple

from evolution.core.utils import lmap
from evolution.core.card import BaseCard
from evolution.core.species import BaseSpecies
from evolution.core.player import BasePlayer
from evolution.core.trait import Trait
from evolution.core.utils import assert_list_with_size, is_natural, is_nat


class Player(BasePlayer):

    @staticmethod
    def _validate_jplayer(jplayer):
        """validates that a given jplayer according to the JSON spec

        :param jplayer: JSON representation of the player to validate
        :type jplayer: JPlayer

        :raises: ValueError if the jplayer does not match the spec
        """

        assert_list_with_size(jplayer, 3, 'jplayer')
        [bag, jboards, jcards] = jplayer

        if not is_natural(bag):
            raise ValueError('bag must be a natural')
        if not isinstance(jboards, list):
            raise ValueError('species must be a list')
        if not isinstance(jcards, list):
            raise ValueError('cards must be a list')

    @classmethod
    def from_json(cls, jplayer):
        cls._validate_jplayer(jplayer)
        [bag, jboards, jcards] = jplayer

        boards = lmap(Species.from_json, jboards)
        cards = [Card.from_json(jcard) for jcard in jcards]

        return cls(id=1, boards=boards, bag=bag, cards=cards)


class Opponent(namedtuple('Opponent', ['boards'])):

    @classmethod
    def from_json(cls, jboards):
        boards = lmap(Species.from_json, jboards)
        return cls(boards)

    def to_json(self):
        return [species.to_json() for species in self.boards]


class Species(BaseSpecies):
    """
    A JSpecies is a [["food", JNat],
                     ["body", JNat],
                     ["population", JNat],
                     ["traits", JLOT]]
    Interpretation:
        - 'food' is a JNat that represents the amount of food tokens on the species
        - 'body' is a JNat that represents the body size of the species
        - 'population' is a JNat that represnts the population of the species
        - 'traits' is a list of JTraits that represent the traits cards on the
           species.
    A JSpecies+ is one of:
        - A JSpecies
        - A JSpecies plus a ["fat-food", JNat]
    Interpretation:
        - 'fat-food' is a JNat that represents how much food is stored on the
           species' 'fat-tissue'.
            - The value will be 0 if the species does not have the 'fat-tissue'
              trait.
        - A JSpecies+ with a 0-valued "fat-food" field renders as a plain Species.
    """

    MIN_POPULATION, MAX_POPULATION = 1, 7
    MIN_BODY, MAX_BODY = 0, 7
    JSPECIES_SIZES = [4, 5]
    JPROPERTY_SIZE = 2
    JTRAIT_RANGE = [0, 3]

    def __lt__(self, other):
        """Lexicographic ordering of species"""

        if self.population != other.population:
            return self.population < other.population
        if self.food != other.food:
            return self.food < other.food
        return self.body < other.body

    @staticmethod
    def _validate_jspecies(jspecies):
        assert_list_with_size(jspecies, Species.JSPECIES_SIZES, 'species')
        for prop in jspecies:
            assert_list_with_size(prop, Species.JPROPERTY_SIZE, 'property')

        [
            [food_name, food],
            [body_name, body],
            [population_name, population],
            [traits_name, jtraits],
            *maybe_fat_food
        ] = jspecies

        if not (food_name == 'food' and is_nat(food)):
            raise ValueError('food must be a Nat')
        if not (body_name == 'body' and is_nat(body)):
            raise ValueError('body must be a Nat')
        if not (population_name == 'population' and
                is_nat(population) and
                population >= Species.MIN_POPULATION):
            raise ValueError('population must be a Nat greater than {}'
                             .format(Species.MIN_POPULATION))

        assert_list_with_size(jtraits, Species.JTRAIT_RANGE, 'traits')

    @staticmethod
    def _validate_maybe_fat_food(maybe_fat_food, traits):
        """validates the fat food if it exists

        :param maybe_fat_food: maybe a fat food value
        :type maybe_fat_food: list

        :param traits: traits on the player
        :type traits: list of Trait

        :raises: ValueError if maybe_fat_food does not match the spec
        """

        if maybe_fat_food:
            [fat_food_name, fat_food] = maybe_fat_food[0]
            if not (fat_food_name == 'fat-food' and is_nat(fat_food)):
                raise ValueError('fat food must be a Nat')
            if fat_food > 0 and Trait.fat_tissue not in traits:
                raise ValueError(
                    'fat tissue must be in traits if fat food is > 0')

    @staticmethod
    def _validate_traits(traits):
        """validates the traits to give to the species

        :param traits: traits on the player
        :type traits: list of Trait

        :raises: ValueError if the traits do not match the spec
        """

        if not len(traits) == len(set(traits)):
            raise ValueError('no duplicate traits permitted')

    @classmethod
    def from_json(cls, jspecies):
        """
        :param jspecies: JSON representation of Species
        :type jspecies: JSpecies+

        :returns: species
        :rtype: Species
        """

        cls._validate_jspecies(jspecies)
        [
            [_, food],
            [_, body],
            [_, population],
            [_, jtraits],
            *maybe_fat_food
        ] = jspecies

        traits = lmap(Trait.from_json, jtraits)
        cls._validate_traits(traits)

        cls._validate_maybe_fat_food(maybe_fat_food, traits)
        if maybe_fat_food:
            [_, fat_food] = maybe_fat_food[0]
        else:
            fat_food = 0

        return cls(food, body, population, traits, fat_food)


class Card(BaseCard):

    JCARD_SIZE = 2
    CARNIVORE_FOOD_RANGE = (-8, 8)
    NON_CARNIVORE_FOOD_RANGE = (-3, 3)

    @classmethod
    def from_json(cls, jcard):
        """Convert a JSON card to the internal representation

        :param jcard: JSON representation of the card
        :type jcard: JCard

        :returns: card
        :rtype: Card
        """
        cls._validate_jcard(jcard)
        food, jtrait = jcard

        trait = Trait.from_json(jtrait)
        cls._validate_food(food, trait)

        return cls(food, trait)

    @staticmethod
    def _validate_jcard(jcard):
        """validates a given jcard according to the json spec

        :param jcard: JSON representation of the card to validate
        :type jcard: JCard
        """

        assert_list_with_size(jcard, Card.JCARD_SIZE, 'card')

    @staticmethod
    def _validate_food(food, trait):
        """validates that the food is within an acceptable range

        :param food: number of food tokens on the card
        :type food: int

        :param trait: trait on the card
        :type trait: Trait
        """

        min_food, max_food = (
            Card.CARNIVORE_FOOD_RANGE if trait is Trait.carnivore
            else Card.NON_CARNIVORE_FOOD_RANGE
        )
        if not (type(food) is int and min_food <= food <= max_food):
            raise ValueError(
                'food must be within {} and {}'.format(min_food, max_food))
