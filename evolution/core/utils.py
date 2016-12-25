from operator import itemgetter
import signal


def is_natural(maybe_natural):
    """is the maybe_natural a natural?

    :param maybe_natural: item to check if is a Natural
    :type maybe_natural: Any

    :returns: whether maybe_natural is a Natural
    :rtype: bool
    """

    min_value = 0
    return type(maybe_natural) is int and maybe_natural >= min_value


def is_natural_plus(maybe_natural_plus):
    """is the maybe_natural_plus a Natural+?

    :param maybe_natural_plus: value to check
    :type maybe_natural_plus: Any

    :returns whether maybe_natural_plus is a Natural+
    :rtype: bool
    """

    min_value = 1
    return is_natural(maybe_natural_plus) and maybe_natural_plus >= min_value


def is_nat(maybe_nat):
    """is the maybe_nat a nat?

    :param maybe_nat: item to check if is a Nat
    :type maybe_nat: Any

    :returns: whether maybe_nat is a Nat
    :rtype: bool
    """

    max_value = 7
    return is_natural(maybe_nat) and maybe_nat <= max_value


def lmap(f, seq):
    """creates a version of map that returns a list instead of iterator

    :param f: function to map
    :type f: func

    :param seq: sequence to map over
    :type seq: iterable
    """

    return list(map(f, seq))


def sort_indices(xs):
    """Returns the sorted indices of the given list

    :param xs: list to sort
    :type xs: list of Any

    :returns: sorted indices
    :returns list of int
    """
    return lmap(itemgetter(0), sorted(enumerate(xs), key=itemgetter(1)))


def split_at(xs, i, exclusive=False):
    """splits the given list of xs at index i

    :param xs: list to split
    :type xs: list of any

    :param i: index to split the list at
    :type i: Natural

    :returns: two new lists that excludes the value at i
    :rtype: (list of any, list of any)
    """

    offset = 1 if exclusive else 0
    return xs[:i], xs[i+offset:]


def assert_list_with_size(item, size, name='item'):
    """checks if a given item is a list of a certain size

    types accepted for `size`:
        list => inclusive edges
        >>> assert_list_with_size([1, 2, 3], (1, 5))
        True

        int => exact size
        >>> assert_list_with_size([1, 2, 3], 3)
        True

    :param item: item to check
    :type item: any

    :param size: bounds to check list's length against
    :type size: list or int

    :param name: (optional) item's name to present in errors
    :type name: str

    :raises: ValueError if list length not within the given bounds
    """

    base_err = '{} must be a list'.format(name)
    if not isinstance(item, list):
        raise ValueError(base_err)

    if isinstance(size, int):
        if len(item) != size:
            raise ValueError('{} of size {}'.format(base_err, size))

    if isinstance(size, list):
        start, end = size
        if not start <= len(item) <= end:
            raise ValueError(
                '{} within {} and {}'.format(base_err, start, end))


def get_neighbors(list_, index):
    """Grab the left and right neighbors of the at the index in the given list

    Returns None if the given neighbor does not exist

    :param list_: list to find neighbors in
    :type species_index: list

    :param index: the index from which to find neighbors
    :type index: int

    :returns: left neighbor, right_neighbor
    :rtype: Any, Any
    """

    if index > 0:
        lneighbor = list_[index-1]
    else:
        lneighbor = None

    try:
        rneighbor = list_[index+1]
    except IndexError:
        rneighbor = None

    return lneighbor, rneighbor


def timeout(seconds, exception=TimeoutError):
    """Decorator raises the exception if execution takes longer than seconds

    :param seconds: number of seconds to wait for function execution
    :type seconds: int

    :param exception: (optional) Exception to raise if function takes too long
    :type exception: Exception

    :returns: wrapped function
    :rtype: Any -> Any
    """

    def wraps(fn):
        def inner(*args, **kwargs):
            def handler(signum, frame):
                raise exception
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            ret = fn(*args, **kwargs)
            signal.alarm(0)
            return ret
        return inner
    return wraps
