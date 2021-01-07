import os
import functools


if os.name == 'nt':
    from . import _windows as _mod
else:
    from . import _linux as _mod


def _proxy(f):
    real_f = getattr(_mod, f.__name__, None)
    if real_f:
        return functools.wraps(f)(real_f)
    else:
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            raise NotImplementedError
        return wrapped


@_proxy
def click(*args):
    """
    Performs a mouse click.

    To left-click wherever the mouse is right now:
    >>> click()

    To use a different button:
    - Left click with -1, 'l' or 'L'
    - Middle click with 0, 'm' or 'M'
    - Right click with +1, 'r' or 'R'
    >>> click(1)

    To left-click after moving to some (x, y) from the top-left corner:
    >>> click(120, 240)

    You can use the 'j' prefix to use relative coordinates.
    At least one non-zero value must have the 'j' prefix:
    >>> click(0j, 20j)

    You can use a floating point value to use percentages.
    Note that you can combine this with the 'j' prefix too:
    >>> click(0.2, 0.8)

    To use a different button after moving to ome (x, y):
    >>> click(240, 360, 'm')
    """


@_proxy
def move(x, y):
    """
    Moves the mouse across the screen.

    To move the mouse to (x, y) from the top-left corner:
    >>> move(120, 240)

    You can use the 'j' prefix to use relative coordinates.
    At least one non-zero value must have the 'j' prefix:
    >>> move(0j, 20j)

    You can use a floating point value to use percentages.
    Note that you can combine this with the 'j' prefix too:
    >>> move(0.2, 0.8)
    """


@_proxy
def mouse():
    """
    Returns a named tuple for the current (x, y) coordinates of the mouse
    in screen. This means you can access the fields as result.x and result.y
    as well, or use 'x, y = mouse()'.
    """


@_proxy
def color(x, y):
    """
    Return the `(R, G, B)` color at the given position.
    """


@_proxy
def is_down(key):
    """
    Is the given key being pressed?

    >>> if is_down('h'):
    ...     print('h')
    ... else:
    ...     print('no h :(')
    """


@_proxy
def press(*keys):
    """
    Presses the given key(s).

    You use 'shift', 'ctrl', 'alt' and 'super' to press these control keys.
    You can press more than one key at once joining them by '+' like 'ctrl+d'.
    You can press function keys from 'F1' to 'F12' (upper-case F letter).
    You can use '\b' as backspace.

    >>> press('j')
    >>> press('H', 'i', 'Return')
    >>> press('shift+h')
    >>> press('ctrl+d')
    >>> press('alt+F4')
    >>> press('super')
    """


@_proxy
def write(*texts):
    """
    Writes the given text(s).
    """
    return _mod.write(*texts)
