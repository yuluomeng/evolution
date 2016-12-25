from evolution.core.trait import Trait


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


class BaseSpecies:
    """
    :attr food: amount of food tokens
    :type food: int

    :attr body: body size
    :type body: int

    :attr population: population size
    :type population: int

    :attr traits: associated trait cards
    :type traits: list of Traits

    :attr fat_food: fat food held by the fat tissue trait
        - This value is equal to 0 if the species does not have fat tissue.
    :type fat_food: int
    """

    def __init__(self, food=0, body=0, population=1, traits=None, fat_food=0):
        self.food = food
        self.body = body
        self.population = population
        self.traits = traits or []
        self.fat_food = fat_food

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.population == other.population and
                self.food == other.food and
                self.body == other.body and
                self.traits == other.traits and
                self.fat_food == other.fat_food)

    def __repr__(self):
        return (
            '<Species> food: {self.food}, body:{self.body}, '
            'population: {self.population}, traits:{self.traits}, '
            'fat_food: {self.fat_food}'
            .format(self=self))

    def copy(self):
        """Creates an instance with the same attributes as the species

        :returns: new instance of Species equal to the given species
        :rtype: Species
        """

        return self.__class__(
            self.food,
            self.body,
            self.population,
            self.traits,
            self.fat_food)

    def is_attackable(self, attacker, lneighbor, rneighbor):
        """Is the species attackable given the species boards involved?

        :param attacker: attacking species
        :type attacker: Species

        :param lneighbor: species on left of defending species
        :type lneighbor: Species or None

        :param rneighbor: species on right of defending species
        :type rneighbor: Species or None
        """

        modified_attacker = attacker._as_attacker()

        return not (
            self._protects_self(modified_attacker, lneighbor, rneighbor) or
            self._protected_by_neighbor(
                modified_attacker, lneighbor, rneighbor)
        )

    def _protects_self(self, attacker, lneighbor, rneighbor):
        """Is the species protected from attack by itself?

        :param attacker: attacking species
        :type attacker: Species

        :param lneighbor: species on left of defending species
        :type lneighbor: Species or None

        :param rneighbor: species on right of defending species
        :type rneighbor: Species or None
        """

        hard_shell_bonus = 4
        return any([
            Trait.burrowing in self.traits and self.food == self.population,

            (Trait.climbing in self.traits and
             Trait.climbing not in attacker.traits),

            (Trait.hard_shell in self.traits and
             attacker.body < (self.body + hard_shell_bonus)),

            (Trait.herding in self.traits and
             self.population >= attacker.population),

            (Trait.symbiosis in self.traits and
             rneighbor and rneighbor.body > self.body)
        ])

    def _protected_by_neighbor(self, attacker, lneighbor, rneighbor):
        """Is the species is protected from attack by one of its neighbors

        :param attacker: attacking species
        :type attacker: Species

        :param lneighbor: species on left of defending species
        :type lneighbor: Species or None

        :param rneighbor: species on right of defending species
        :type rneighbor: Species or None
        """

        neighbor_has_warning_call = (
            (lneighbor and Trait.warning_call in lneighbor.traits) or
            (rneighbor and Trait.warning_call in rneighbor.traits))

        return (
            neighbor_has_warning_call and Trait.ambush not in attacker.traits)

    def _as_attacker(self):
        """activates all traits affecting an attacker's attributes

        :returns: new species with modified attacker
        :rtype: Species
        """

        attacker = self.copy()

        if Trait.pack_hunting in attacker.traits:
            attacker.body += attacker.population

        return attacker

    def hunger(self):
        """Food tokens required to make the species full

        :returns: Food tokens required to make the species full
        :rtype: Nat
        """

        return self.population - self.food

    def fat_food_need(self):
        """Need of the fat tissue

        :returns: need of the fat tissue
        :rtype: Nat
        """

        if Trait.fat_tissue in self.traits:
            return self.body - self.fat_food
        return 0

    def to_json(self):
        """Converts a Species to its JSON representation.

        :returns: JSON representation of the Species.
        :rtype: JSpecies
        """
        jspecies = [
            ['food', self.food],
            ['body', self.body],
            ['population', self.population],
            ['traits', [trait.to_json() for trait in self.traits]]
        ]
        if self.fat_food > 0:
            jspecies.append(['fat-food', self.fat_food])
        return jspecies
