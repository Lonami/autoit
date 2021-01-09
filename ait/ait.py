"""
ait
===

Automate it with Python. Move the mouse, click, type things or press key combinations from Python.

Wherever a mouse button is expected, you can use the following values (strings are case insensitive):

- Left click with -1, 'L' or 'LMB'
- Middle click with 0, 'M' or 'MMB'
- Right click with +1, 'R' or 'RMB'

Wherever a key is expected, you can use either the character you want to type (for example, '!').
Note that this includes the following escape sequences:

- Backspace with '\b'
- Enter key with '\n' (not carriage return, which although would make more sense is annoying).
- Tabulator key with '\t'

For special keys, the following strings can be used (case insensitive):

- Left shift with 'SHIFT' or 'LSHIFT', or right shift with 'RSHIFT'
- Left control with 'CTRL' or 'LCTRL', or right control with 'RCTRL'
- Alt ("menu") with 'ALT' or 'LALT', or right alt with 'RALT'
- Super (or "Windows key") with 'SUPER'
- Function keys from 'F1' up to 'F24'
- Caps lock with 'CAPSLOCK'
- Num lock with 'NUMLOCK'
- Scroll lock with 'SCROLLLOCK'
- Escape with 'ESC'
- Page up ("prior") with 'PAGEUP'
- Page down ("next") with 'PAGEDOWN'
- End with 'END'
- Home with 'HOME'
- Left arrow with 'LEFT'
- Up arrow with 'UP'
- Right arrow with 'RIGHT'
- Down arrow with 'DOWN'
- Insert with 'INS'
- Delete with 'DEL'
- Print screen with 'PRSCR'
- Mute with 'MUTE'
- Volumen down with 'VOLDOWN'
- Volumen up with 'VOLUP'
- Next media with 'MEDIANEXT'
- Previous media with 'MEDIAPREV'
- Stop media with 'MEDIASTOP'
- Play/pause media with 'MEDIAPLAYPAUSE'
"""
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


# Mouse


@_proxy
def mouse():
    """
    Returns a named tuple for the current `(x, y)` coordinates of the mouse in screen.

    The coordinates are absolute and start from `(0, 0)` at the top-left of the screen.
    This means that the left-most `x` coordinate will be 0, the right-most the screen width
    minus one, the top-most `y` will be 0, and the bottom-most the screen height minus one.

    >>> pos = mouse()
    >>> print(pos.x, pos.y)

    Or:

    >>> (x, y) = mouse()
    """


@_proxy
def move(x, y):
    """
    Moves the mouse across the screen.

    You can use integers to mean absolute coordinates from the top-left corner.
    To move the mouse to `(x, y)`:

    >>> move(120, 240)

    You can use the 'j' prefix to mean relative coordinates.
    At least one non-zero value must have the 'j' prefix:

    >>> move(0j, 20j)

    You can use a floating point value to mean percentages.
    Note that you can combine this with the 'j' prefix too:

    >>> move(0.2, 0.8)
    """


@_proxy
def click(*args):
    """
    Performs a mouse click.

    To left-click wherever the mouse is right now:

    >>> click()

    To use a different button, like right-click:

    >>> click(1)

    To left-click after moving to some `(x, y)` from the top-left corner:

    >>> click(120, 240)

    You can also use all the movement options from `move` for `click`.

    To use a different button after moving to some `(x, y)`:

    >>> click(240, 360, 'm')
    """


# Keyboard


@_proxy
def press(*keys):
    """
    Presses the given key(s).

    >>> press('j')
    >>> press('H', 'i', '\n')
    >>> press('super')

    You can press more than one key at once joining them by '+' like 'ctrl+d', which is equivalent
    to using `hold` for all the keys except the last one and then `press` on that last key.

    >>> press('shift+h')
    >>> press('ctrl+d')
    >>> press('alt+F4')
    """


@_proxy
def hold(*keys):
    """
    Return an object to be used as a context-manager that will hold the given
    keys for as long as it's open.

    For example, you can use this to control-click:

    >>> with hold('ctrl'):
    >>>     click()

    Or more complicated combinations such as opening the Windows task manager:

    >>> with hold('ctrl', 'shift'):
    >>>     press('esc')
    """


def write(*texts, sep=' ', end=''):
    """
    Type the given text(s) as they are, as fast as possible.

    >>> write('Hello, world!')

    `sep` and `end` behave like they do in `print`, but `end` defaults to the empty string instead.

    >>> write('Hello', 'world!', sep=' ... ', end='\n')
    """
    _mod.write(sep.join(texts) + end)


@_proxy
def events():
    """
    Return an iterator over the keyboard and mouse button events.

    The yielded items are tuples consisting of `(key, down)`, where `key` is the uppercase string
    representing the key and `down` is a boolean which is `True` if the key is being held.

    >>> for key, down in events():
    ...     if key == 'H' and down:
    ...         print('h!')

    The iterator can also be used in asynchronous contexts (`async for`).

    If multiple events occured between iteration steps, they're returned in arbitrary order.
    """


# Mouse-keyboard common


@_proxy
def holding(key):
    """
    Is the given key being held?

    >>> if holding('h'):
    ...     print('h')
    ... else:
    ...     print('no h :(')

    Note that you can use this for mouse buttons with the 'LMB' notation:

    >>> if holding('lmb'):
    ...     print('dragging something')
    ... else:
    ...     print('left mouse button not being held')
    """


# Clipboard


@_proxy
def paste():
    """
    Paste the current clipboard contents into a Python `str` and return it.

    If you want to emulate pressing `Ctrl+V`, use `press` instead.

    >>> clipboard = paste()
    >>> print(clipboard)
    """


@_proxy
def copy(text):
    """
    Copy the given input text into the system's clipboard.

    If you want to emulate pressing `Ctrl+C`, use `press` instead.

    >>> copy('meow')
    """


# Screen-related functions


@_proxy
def size():
    """
    Returns a named tuple for the primary screen's `(width, height)`:

    >>> dim = size()
    >>> aspect_ratio = dim.width / dim.height
    """


def color(*args):
    """
    Returns a named tuple for the  `(r, g, b)` color at the current mouse position:

    >>> rgb = color()
    >>> print(rgb.r)

    Or, if a position is given:

    >>> r, g, b = color(100, 200)
    >>> print(g)
    """
    argc = len(args)
    if argc == 0:
        x, y = mouse()
    elif argc == 2:
        x, y = args
    else:
        raise TypeError('0 or 2 arguments required, but {} given'.format(argc))

    return _mod.color(x, y)
