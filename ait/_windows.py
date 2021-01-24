import ctypes
import sys
import time
import functools
from ctypes.wintypes import HANDLE, BOOL, HWND, UINT, HGLOBAL, LPVOID
from contextlib import contextmanager
import asyncio
from ._common import Position, Color, MB

EVENTS_POLL_DELAY = 0.05

NO_ERROR = 0

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x0002


MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040


# https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes
KEYS = [
    (),
    ('LMB',),
    ('RMB',),
    ('CANCEL',),
    ('MMB',),
    ('X1MB',),
    ('X2MB',),
    (),
    ('\b',),
    ('\t',),
    (),
    (),
    ('CLEAR',),
    ('\n',),
    (),
    (),
    ('SHIFT',),
    ('CTRL',),
    ('ALT',),
    ('PAUSE',),
    ('CAPSLOCK',),
    ('IMEKANA', 'IMEHANGUL',),
    ('IMEON',),
    ('IMEJUNJA',),
    ('IMEFINAL',),
    ('IMEHANJA', 'IMEKANJI',),
    ('IMEOFF',),
    ('ESC',),
    ('IMECONVERT',),
    ('IMENONCONVERT',),
    ('IMEACCEPT',),
    ('IMEMODECHANGE',),
    (' ',),
    ('PAGEUP',),
    ('PAGEDOWN',),
    ('END',),
    ('HOME',),
    ('LEFT',),
    ('UP',),
    ('RIGHT',),
    ('DOWN',),
    ('SELECT',),
    ('PRINT',),
    ('EXECUTE',),
    ('PRINTSCR',),
    ('INS',),
    ('DEL',),
    ('HELP',),
    ('0',),
    ('1',),
    ('2',),
    ('3',),
    ('4',),
    ('5',),
    ('6',),
    ('7',),
    ('8',),
    ('9',),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    ('A',),
    ('B',),
    ('C',),
    ('D',),
    ('E',),
    ('F',),
    ('G',),
    ('H',),
    ('I',),
    ('J',),
    ('K',),
    ('L',),
    ('M',),
    ('N',),
    ('O',),
    ('P',),
    ('Q',),
    ('R',),
    ('S',),
    ('T',),
    ('U',),
    ('V',),
    ('W',),
    ('X',),
    ('Y',),
    ('Z',),
    ('SUPER', 'LSUPER'),
    ('RSUPER',),
    ('APPS',),
    (),
    ('SLEEP',),
    ('N0',),
    ('N1',),
    ('N2',),
    ('N3',),
    ('N4',),
    ('N5',),
    ('N6',),
    ('N7',),
    ('N8',),
    ('N9',),
    ('MUL',),
    ('ADD',),
    ('SEPARATOR',),
    ('SUB',),
    ('DECIMAL',),
    ('DIV',),
    ('F1',),
    ('F2',),
    ('F3',),
    ('F4',),
    ('F5',),
    ('F6',),
    ('F7',),
    ('F8',),
    ('F9',),
    ('F10',),
    ('F11',),
    ('F12',),
    ('F13',),
    ('F14',),
    ('F15',),
    ('F16',),
    ('F17',),
    ('F18',),
    ('F19',),
    ('F20',),
    ('F21',),
    ('F22',),
    ('F23',),
    ('F24',),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    ('NUMLOCK',),
    ('SCROLLLOCK',),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    ('LSHIFT',),
    ('RSHIFT',),
    ('LCTRL',),
    ('RCTRL',),
    ('LALT',),
    ('RALT',),
    ('BACK',),
    ('FORWARD',),
    ('REFRESH',),
    ('STOP',),
    ('SEARCH',),
    ('FAVORITES',),
    ('LANDPAGE',),
    ('MUTE',),
    ('VOLDOWN',),
    ('VOLUP',),
    ('MEDIANEXT',),
    ('MEDIAPREV',),
    ('MEDIASTOP',),
    ('MEDIATOGGLE',),
    ('MAIL',),
    ('MEDIASELECT',),
    ('APP1',),
    ('APP2',),
    (),
    (),
    ('OEM1',),
    ('OEMPLUS',),
    ('OEMCOMMA',),
    ('OEMMINUS',),
    ('OEMPERIOD',),
    ('OEM2',),
    ('OEM3',),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    ('OEM4',),
    ('OEM5',),
    ('OEM6',),
    ('OEM7',),
    ('OEM8',),
    (),
    ('OEMA',),
    ('OEM102',),
    ('OEMB',),
    ('OEMC',),
    ('IMEPROCESS',),
    ('OEMD',),
    ('PACKET',),
    (),
    ('OEME',),
    ('OEMF',),
    ('OEMG',),
    ('OEMH',),
    ('OEMI',),
    ('OEMJ',),
    ('OEMK',),
    ('OEML',),
    ('OEMM',),
    ('OEMN',),
    ('OEMO',),
    ('OEMP',),
    ('OEMQ',),
    ('ATTN',),
    ('CRSEL',),
    ('EXSEL',),
    ('EREOF',),
    ('PLAY',),
    ('ZOOM',),
    (),
    ('PA1',),
    ('OEMCLEAR',),
    (),
]

KEY_MAP = {name: vk for vk, names in enumerate(KEYS) for name in names}

BUTTON_TO_EVENTS = {
    MB.L: (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    MB.R: (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    MB.M: (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040


def _key_to_vk(key):
    key = key.strip().upper()
    try:
        return KEY_MAP[key]
    except KeyError:
        try:
            # TODO VkKeyScanExA
            return ord(key)
        except TypeError:
            raise ValueError('Unknown key {!r}'.format(key)) from None


def _vk_to_key(vk):
    try:
        return KEYS[vk][0]
    except KeyError:
        return ValueError('Unknown virtual key {!r}'.format(vk))


def _vk_to_kbd_input(vk, down):
    return INPUT(type=INPUT_KEYBOARD, value=INPUTUNION(ki=KEYBDINPUT(
        wVk=vk,
        wScan=0,
        dwFlags=(KEYEVENTF_KEYUP, 0)[down],
        time=0,
        dwExtraInfo=None
    )))


def _key_as_kbd_inputs(key):
    vks = list(map(_key_to_vk, key.split('+')))
    for vk in vks:
        yield _vk_to_kbd_input(vk, True)
    for vk in reversed(vks):
        yield _vk_to_kbd_input(vk, False)


# ctypes is broken for pointers. ctypes.windll.* functions can be patched in-place but it's simpler not to.
# https://forums.autodesk.com/t5/maya-programming/ctypes-bug-cannot-copy-data-to-clipboard-via-python/td-p/9195866
def _define(fn, res, *args):
    fn.argtypes = args
    fn.restype = res
    return fn


user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

OpenClipboard = _define(user32.OpenClipboard, BOOL, HWND)
CloseClipboard = _define(user32.CloseClipboard, BOOL)

EmptyClipboard = _define(user32.EmptyClipboard, BOOL)

GetClipboardData = _define(user32.GetClipboardData, HANDLE, UINT)
SetClipboardData = _define(user32.SetClipboardData, HANDLE, UINT, HANDLE)

GlobalLock = _define(kernel32.GlobalLock, LPVOID, HGLOBAL)
GlobalUnlock = _define(kernel32.GlobalUnlock, BOOL, HGLOBAL)
GlobalAlloc = _define(kernel32.GlobalAlloc, HGLOBAL, UINT, ctypes.c_size_t)
GlobalSize = _define(kernel32.GlobalSize, ctypes.c_size_t, HGLOBAL)



@functools.lru_cache(1)
def _get_screen_size():
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsystemmetrics
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1
    width = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
    height = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
    return width, height


def _parse_pos(x, y):
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput
    MAX = 65535

    rel = bool(x.imag or y.imag)
    if rel:
        x = x.imag or x.real
        y = y.imag or y.real

    if not (0.0 < x < 1.0 or 0.0 < y < 1.0):
        w, h = _get_screen_size()
        x /= w
        y /= h

    x *= MAX
    y *= MAX
    return int(x), int(y), rel


class DCBox:
    def __init__(self):
        self.desktop = ctypes.windll.user32.GetDC(0)

    def __del__(self):
        ctypes.windll.user32.ReleaseDC(self.desktop)


DC_BOX = DCBox()


class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

    def __str__(self):
        return f'{self.x} {self.y}'


class MOUSEINPUT(ctypes.Structure):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-tagmouseinput
    typedef struct tagMOUSEINPUT {
        LONG      dx;
        LONG      dy;
        DWORD     mouseData;
        DWORD     dwFlags;
        DWORD     time;
        ULONG_PTR dwExtraInfo;
    } MOUSEINPUT, *PMOUSEINPUT, *LPMOUSEINPUT;
    """
    _fields_ = [
        ('dx', ctypes.c_long),
        ('dy', ctypes.c_long),
        ('mouseData', ctypes.c_long),
        ('dwFlags', ctypes.c_long),
        ('time', ctypes.c_long),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


class KEYBDINPUT(ctypes.Structure):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-tagkeybdinput
    typedef struct tagKEYBDINPUT {
        WORD      wVk;
        WORD      wScan;
        DWORD     dwFlags;
        DWORD     time;
        ULONG_PTR dwExtraInfo;
    } KEYBDINPUT, *PKEYBDINPUT, *LPKEYBDINPUT;
    """
    _fields_ = [
        ('wVk', ctypes.c_short),
        ('wScan', ctypes.c_short),
        ('dwFlags', ctypes.c_long),
        ('time', ctypes.c_long),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]


class HARDWAREINPUT(ctypes.Structure):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-taghardwareinput
    typedef struct tagHARDWAREINPUT {
        DWORD uMsg;
        WORD  wParamL;
        WORD  wParamH;
    } HARDWAREINPUT, *PHARDWAREINPUT, *LPHARDWAREINPUT;
    """
    _fields_ = [
        ('uMsg', ctypes.c_long),
        ('wParamL', ctypes.c_short),
        ('wParamH', ctypes.c_short)
    ]


class INPUTUNION(ctypes.Union):
    # See INPUT
    _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/ns-winuser-taginput
    typedef struct tagINPUT {
        DWORD type;
        union {
            MOUSEINPUT    mi;
            KEYBDINPUT    ki;
            HARDWAREINPUT hi;
        } DUMMYUNIONNAME;
    } INPUT, *PINPUT, *LPINPUT;
    """
    _fields_ = [('type', ctypes.c_long), ('value', INPUTUNION)]


# Mouse


def mouse():
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getcursorpos
    BOOL GetCursorPos(
        LPPOINT lpPoint
    );
    Returns x, y as int
    """
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return Position(pt.x, pt.y)



def move(x, y):
    x, y, rel = _parse_pos(x, y)
    MOUSEEVENTF_ABSOLUTE = 0x8000
    MOUSEEVENTF_MOVE = 0x0001
    inputs = INPUT(type=INPUT_MOUSE, value=INPUTUNION(mi=MOUSEINPUT(
        dx=x,
        dy=y,
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE | (MOUSEEVENTF_ABSOLUTE, 0)[rel],
        time=0,
        dwExtraInfo=None,
    )))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(inputs))


def click(*args):
    argc = len(args)
    if argc == 0:
        button = MB.L
    elif argc == 1:
        button = MB.parse(args[0])
    elif argc == 3:
        x, y, button = args
        button = MB.parse(button)
        # TODO move mouse with the call directly
        move(x, y)
    else:
        raise TypeError('0, 1 or 3 arguments required, but {} given'.format(argc))

    flags = BUTTON_TO_EVENTS[button]
    count = ctypes.c_uint(1)
    for flag in flags:
        inputs = INPUT(type=INPUT_MOUSE, value=INPUTUNION(mi=MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=0,
            dwFlags=flag,
            time=0,
            dwExtraInfo=None,
        )))
        ctypes.windll.user32.SendInput(count, ctypes.byref(inputs), ctypes.sizeof(inputs))


# Keyboard


def press(*keys):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-sendinput
    UINT SendInput(
        UINT    cInputs,
        LPINPUT pInputs,
        int     cbSize
    );
    """
    inputs = [i for key in keys for i in _key_as_kbd_inputs(key)]
    count = len(inputs)
    inputs = (INPUT * count)(*inputs)
    ctypes.windll.user32.SendInput(count, inputs, ctypes.sizeof(INPUT))


@contextmanager
def hold(*keys):
    count = len(keys)
    inputs = (INPUT * count)(*(_vk_to_kbd_input(_key_to_vk(key), True) for key in keys))
    ctypes.windll.user32.SendInput(count, inputs, ctypes.sizeof(INPUT))
    try:
        yield
    finally:
        inputs = (INPUT * count)(*(_vk_to_kbd_input(_key_to_vk(key), False) for key in keys))
        ctypes.windll.user32.SendInput(count, inputs, ctypes.sizeof(INPUT))


class _Events:
    def __init__(self):
        self._before = ctypes.create_string_buffer(256)
        self._after = ctypes.create_string_buffer(256)
        self._events = []

    @staticmethod
    def _refetch(buffer):
        # `GetKeyState` before `GetKeyboardState` seems to be needed for some reason.
        ctypes.windll.user32.GetKeyState(0)
        ctypes.windll.user32.GetKeyboardState(buffer)
        buffer.raw = bytes(x & 0x80 for x in buffer.raw)

    def _fill_events(self):
        self._refetch(self._after)

        for vk, (b, a) in enumerate(zip(self._before.raw, self._after.raw)):
            if b != a:
                self._events.append((_vk_to_key(vk), bool(a)))

        self._before, self._after = self._after, self._before

    def __iter__(self):
        self._refetch(self._before)
        return self

    def __next__(self):
        if not self._events:
            self._fill_events()
            while not self._events:
                time.sleep(EVENTS_POLL_DELAY)
                self._fill_events()

        return self._events.pop()

    def __aiter__(self):
        self._refetch(self._before)
        return self

    async def __anext__(self):
        if not self._events:
            self._fill_events()
            while not self._events:
                await asyncio.sleep(EVENTS_POLL_DELAY)
                self._fill_events()

        return self._events.pop()


def events():
    return _Events()


# Mouse-keyboard common


def holding(vk):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeystate
    SHORT GetKeyState(
        int nVirtKey
    );
    """
    return (ctypes.windll.user32.GetKeyState(vk) & 0x80) != 0


def color(x, y):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/wingdi/nf-wingdi-getpixel
    COLORREF GetPixel(
        HDC hdc,
        int x,
        int y
    );
    Returns colors as zbgr int
    """
    zbgr = ctypes.windll.gdi32.GetPixel(DC_BOX.desktop, x, y)
    return Color(
        (zbgr >> 0) & 0xff,
        (zbgr >> 8) & 0xff,
        (zbgr >> 16) & 0xff,
    )


# Clipboard


def paste():
    OpenClipboard(None)
    handle = GetClipboardData(CF_UNICODETEXT)
    cstring = GlobalLock(handle)
    size = GlobalSize(handle)
    if cstring and size:
        raw_data = ctypes.create_string_buffer(size)
        # (ctypes.c_byte * size).from_address(cstring)[:] would give us a (less efficient) Python list.
        # bytes.decode does not seem happy taking c_byte_Array_# as input parameter unfortunately.
        # Using a temporary buffer for strings and moving the data seems to be the best approach.
        ctypes.memmove(raw_data, cstring, size)
        text = raw_data.raw.decode('utf-16le').rstrip('\0')
    else:
        text = None

    GlobalUnlock(handle)
    CloseClipboard()
    return text


def copy(text):
    buffer = text.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(buffer) + 2)
    cstring = GlobalLock(handle)
    ctypes.memmove(cstring, buffer, len(buffer))
    GlobalUnlock(handle)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard()


# Screen
