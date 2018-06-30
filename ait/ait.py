import functools
import subprocess
from collections import namedtuple

try:
    import screeninfo
except ImportError:
    screeninfo = None

from .logger import Logger

BUTTONS = {
    # Left
    -1: '1',
    'l': '1',
    'L': '1',
    # Middle
    0: '2',
    'r': '2',
    'R': '2',
    # Right
    1: '3',
    'm': '3',
    'M': '3',
}

KEYS = {
    ' ': 'space',
    '!': 'exclam',
    '"': 'quotedbl',
    '#': 'numbersign',
    '$': 'dollar',
    '%': 'percent',
    '&': 'ampersand',
    "'": 'quoteright',
    '(': 'parenleft',
    ')': 'parenright',
    '[': 'bracketleft',
    '*': 'asterisk',
    '\\': 'backslash',
    '+': 'plus',
    ']': 'bracketright',
    ',': 'comma',
    '^': 'asciicircum',
    '-': 'minus',
    '_': 'underscore',
    '.': 'period',
    '`': 'quoteleft',
    '/': 'slash',
    ':': 'colon',
    ';': 'semicolon',
    '<': 'less',
    '=': 'equal',
    '>': 'greater',
    '?': 'question',
    '@': 'at',
    '{': 'braceleft',
    '|': 'bar',
    '}': 'braceright',
    '~': 'asciitilde',
    '\b': 'BackSpace',
    '\n': 'Return'
}

Position = namedtuple('Position', ('x', 'y'))


def _parse_button(n):
    try:
        return BUTTONS[n]
    except KeyError:
        raise ValueError('Invalid button given') from None


@functools.lru_cache(1)
def _get_screen_size():
    if screeninfo is None:
        raise ValueError('screeninfo must be installed to use % positions')

    monitor = screeninfo.get_monitors()[0]
    _screen_size = (monitor.width, monitor.height)
    return _screen_size


def _parse_pos(x, y):
    rel = x.imag or y.imag
    if rel:
        x = x.imag or x.real
        y = y.imag or y.real

    if 0.0 < x < 1.0 or 0.0 < y < 1.0:
        w, h = _get_screen_size()
        if 0.0 < x < 1.0:
            x = int(w * x)
        if 0.0 < y < 1.0:
            y = int(h * y)

    return str(int(x)), str(int(y)), rel


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
    argc = len(args)
    assert argc < 4, 'Invalid number of arguments'
    if argc & 2:
        move(args[0], args[1])

    button = _parse_button(args[-1]) if argc & 1 else '1'
    subprocess.run(('xdotool', 'click', button))


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
    x, y, rel = _parse_pos(x, y)
    move_arg = 'mousemove_relative' if rel else 'mousemove'
    subprocess.run(('xdotool', move_arg, x, y))


def mouse():
    """
    Returns a named tuple for the current (x, y) coordinates of the mouse
    in screen. This means you can access the fields as result.x and result.y
    as well, or use 'x, y = mouse()'.
    """
    output = subprocess.run(('xdotool', 'getmouselocation'),
                            stdout=subprocess.PIPE).stdout

    end = output.index(b' ', 3)  # Start at 'x:_'
    x = int(output[2:end])
    y = int(output[end + 3:output.index(b' ', end + 4)])
    return Position(x, y)


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
    args = ['xdotool', 'key']
    args.extend(KEYS.get(k, k) for k in keys)
    subprocess.run(args)


def write(*texts):
    """
    Writes the given text(s).
    """
    args = ['xdotool', 'type']
    args.extend(texts)
    subprocess.run(args)


log = Logger()
