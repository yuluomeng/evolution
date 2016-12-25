"""
A JPlayer is a [["id", JNatural+],
                ["species", JLOS],
                ["bag", JNatural]]
Interpretation:
    - "id" represents a unique identifier for the JPlayer.
    - "species" represents the ordered list of species the Player owns.
    - "bag" represents tha amount of tokens in the JPlayer's food bag.

A JPlayer+ is one of:
    - A JPlayer
    - A JPlayer plus a ["cards", JLOC]
Interpretation:
    - "cards" is a LOC that represents the cards held in the JPlayer's hand.
    - A JPlayer+ with a []-valued "cards" field renders as a plain JPlayer.
    - None of a JPlayer+'s species may have a population of 0.
"""


class BasePlayer:
    """
    :attr _id: id that is unqiue to each player
    :type _id: Natural+

    :attr boards: species boards
    :type boards: list of Species

    :attr bag: amount of tokens in the food bag
    :type bag: Natural

    :attr cards: cards held in the player's hand
    :type cards: list of Card
    """

    def __init__(self, id=None, boards=None, bag=0, cards=None):
        self._id = id
        self.boards = boards or []
        self.bag = bag
        self.cards = cards or []

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self._id == other._id and
                self.boards == other.boards and
                self.bag == other.bag and
                self.cards == other.cards)
