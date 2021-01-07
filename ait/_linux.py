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


def _requires(*, program, message):
    """
    Decorator that replaces methods with a no-op raise error function
    if the desired condition (such as a program running successfully)
    is not met.
    """
    try:
        subprocess.run(program, shell=True, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        ok = False
    else:
        ok = True

    def decorator(f):
        if ok:
            return f
        else:
            @functools.wraps(f)
            def failed(*args, **kwargs):
                raise ValueError(message)
            return failed

    return decorator


_requires_xdotool = _requires(program='xdotool -v',
                              message='xdotool is not installed')


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


@_requires_xdotool
def click(*args):
    argc = len(args)
    assert argc < 4, 'Invalid number of arguments'
    if argc & 2:
        move(args[0], args[1])

    button = _parse_button(args[-1]) if argc & 1 else '1'
    subprocess.run(('xdotool', 'click', button))


@_requires_xdotool
def move(x, y):
    x, y, rel = _parse_pos(x, y)
    move_arg = 'mousemove_relative' if rel else 'mousemove'
    subprocess.run(('xdotool', move_arg, x, y))


@_requires_xdotool
def mouse():
    output = subprocess.run(('xdotool', 'getmouselocation'),
                            stdout=subprocess.PIPE).stdout

    end = output.index(b' ', 3)  # Start at 'x:_'
    x = int(output[2:end])
    y = int(output[end + 3:output.index(b' ', end + 4)])
    return Position(x, y)


@_requires_xdotool
def press(*keys):
    args = ['xdotool', 'key']
    args.extend(KEYS.get(k, k) for k in keys)
    subprocess.run(args)


@_requires_xdotool
def write(*texts):
    args = ['xdotool', 'type']
    args.extend(texts)
    subprocess.run(args)


try:
    log = Logger()
except ValueError:
    log = None
