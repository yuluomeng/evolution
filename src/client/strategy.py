from operator import itemgetter

from evolution.core.trait import Trait
from evolution.core.utils import get_neighbors, sort_indices
from evolution.client.action import (
    AddToWateringHole, AddSpecies, AddPopulation, AddBody, ReplaceTrait)
from evolution.client.feeding import (
    NoFeeding, FatTissueFeeding, CarnivoreFeeding, VegetarianFeeding)


def play_cards(player, boards_before, boards_after):
    """get card play actions for the player

    :returns: the actions a player wishes to make
    :rtype: JAction
    """

    new_species_index = len(player.boards)
    sorted_card_indices = sort_indices(player.cards)

    actions = {}
    actions.update({
        AddToWateringHole: AddToWateringHole(sorted_card_indices[0]),
        AddSpecies: [
            AddSpecies(sorted_card_indices[1], [sorted_card_indices[2]])
        ],
        AddPopulation: [
            AddPopulation(new_species_index, sorted_card_indices[3])
        ]
    })
    if len(player.cards) > 4:
        actions.update({
            AddBody: [
                AddBody(new_species_index, sorted_card_indices[4])
            ]
        })
    if len(player.cards) > 5:
        actions.update({
            ReplaceTrait: [
                ReplaceTrait(new_species_index, 0, sorted_card_indices[5])
            ]
        })

    return actions


def feedNext(player, watering_hole, opponents):
    """Picks a species to feed for the player in the given feeding.

    :param player: current player which needs to be fed
    :type player: Player

    :param watering_hole: number of tokens remaining on the watering_hole
    :param watering_hole: Natural+

    :param opponents: opponents to potentially attack
    :type opponents: list of Opponent

    :returns: player's choice of feeding
    :rtype: Feeding
    """

    return (feed_fat_tissue(player.boards, watering_hole) or
            feed_vegetarian(player.boards) or
            feed_carnivore(player.boards, opponents) or
            NoFeeding())


def feed_fat_tissue(boards, watering_hole):
    """Select a fat tissue species to feed if possible

    :param boards: all species boards a player owns
    :type boards: list of Species

    :param watering_hole: number of tokens at the watering hole
    :type watering_hole: Natural+

    :returns: fat tissue feeding if the player can feed
    :rtype: FatTissueFeeding or None
    """

    fat_tissue_boards = [
        (i, species, species.fat_food_need())
        for i, species in enumerate(boards)
        if species.fat_food_need() > 0
    ]
    if not fat_tissue_boards:
        return None

    species_index, _, fat_food_need = max(
        fat_tissue_boards, key=lambda x: (x[2], x[1]))

    if fat_food_need > 0:
        return FatTissueFeeding(
            species_index, min(fat_food_need, watering_hole))
    return None


def feed_vegetarian(boards):
    """Select a vegetarian to feed if possible

    :param boards: all species boards a player owns
    :type boards: list of Species

    :returns: vegetarian feeding if player can feed
    :rtype: VegetarianFeeding or None
    """

    hungry_vegetarians = [
        (i, species) for i, species in enumerate(boards)
        if Trait.carnivore not in species.traits and species.hunger() > 0
    ]
    if not hungry_vegetarians:
        return None

    species_index, _ = max(hungry_vegetarians, key=itemgetter(1))
    return VegetarianFeeding(species_index)


def feed_carnivore(boards, opponents):
    """Select a carnivore to feed if possible

    :param boards: all species boards a player owns
    :type boards: list of Species

    :param opponents: opponents to potentially attack
    :type opponents: list of Opponent

    :returns: carnivore feeding if player can feed
    :rtype: CarnivoreFeeding or None
    """

    hungry_carnivores = [
        (i, species) for i, species in enumerate(boards)
        if Trait.carnivore in species.traits and species.hunger() > 0
    ]
    if not hungry_carnivores:
        return None

    attacker_index, attacker = max(hungry_carnivores, key=itemgetter(1))

    opponent_index = defending_species = defending_species_index = None
    for i, opponent in enumerate(opponents):
        target_species, target_species_index = choose_target(
            attacker, opponent)
        if not target_species:
            continue
        if not defending_species or defending_species < target_species:
            defending_species = target_species
            defending_species_index = target_species_index
            opponent_index = i

    if defending_species:
        return CarnivoreFeeding(
            attacker_index, opponent_index, defending_species_index)
    return None


def choose_target(attacker, opponent):
    """Pick a species for the attacker to attack

    :param attacker: species that will attack
    :type attacker: Species

    :param opponent: player whose species are being attacked.
    :type opponent: Opponent

    :returns: species that would be attacked
    :rtype: Species or None
    """

    target = target_index = None
    for index, defender in enumerate(opponent.boards):
        lneighbor, rneighbor = get_neighbors(opponent.boards, index)
        if not defender.is_attackable(attacker, lneighbor, rneighbor):
            continue
        if not target or target < defender:
            target = defender
            target_index = index
    return target, target_index
