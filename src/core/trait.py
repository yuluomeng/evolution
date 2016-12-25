from enum import Enum


class TraitEnum(Enum):

    def __lt__(self, other):
        return self.name < other.name

    @classmethod
    def from_json(cls, jtrait):
        """creates a Trait variant from the JSON representation

        :param jtrait: JSON representation of a Trait
        :type jtrait: JTrait

        :returns: TraitEnum variant
        :rtype: Trait
        """

        if not isinstance(jtrait, str):
            raise ValueError('jtrait must be of type str')
        try:
            return cls[jtrait.replace('-', '_')]
        except KeyError:
            raise ValueError('{} is not a valid jtrait'.format(jtrait))

    def to_json(self):
        """returns the JSON representation of a Trait

        :returns: JSON representation of a Trait
        :rtype: JTrait
        """

        return self.name.replace('_', '-')


Trait = TraitEnum('Trait', [
    'carnivore',
    'ambush',
    'burrowing',
    'climbing',
    'cooperation',
    'fat_tissue',
    'fertile',
    'foraging',
    'hard_shell',
    'herding',
    'horns',
    'long_neck',
    'pack_hunting',
    'scavenger',
    'symbiosis',
    'warning_call'
])
