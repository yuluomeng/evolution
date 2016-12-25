
from evolution.client.dealer_proxy import Turn


def test_is_valid_transition():

    unstarted = Turn.unstarted
    assert unstarted.is_valid_transition(Turn.unstarted) is True
    assert unstarted.is_valid_transition(Turn.start) is True
    assert unstarted.is_valid_transition(Turn.choose) is False

    start = Turn.start
    assert start.is_valid_transition(Turn.choose) is True
    assert start.is_valid_transition(Turn.feedNext) is False

    choose = Turn.choose
    assert choose.is_valid_transition(Turn.feedNext) is True
    assert choose.is_valid_transition(Turn.start) is True
    assert choose.is_valid_transition(Turn.choose) is False

    feed_next = Turn.feedNext
    assert feed_next.is_valid_transition(Turn.start) is True
    assert feed_next.is_valid_transition(Turn.feedNext) is True
    assert feed_next.is_valid_transition(Turn.choose) is False


def test_from_msg():

    assert Turn.from_msg('ok') == Turn.unstarted
    assert Turn.from_msg([2, 3, [], []]) == Turn.start
    assert Turn.from_msg([[], []]) == Turn.choose
    assert Turn.from_msg([3, [], [], 2, []]) == Turn.feedNext
