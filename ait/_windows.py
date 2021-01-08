import ctypes
import sys
import time
import functools
from ctypes.wintypes import HANDLE, BOOL, HWND, UINT, HGLOBAL, LPVOID
from contextlib import contextmanager
from ._common import Position, Color

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


# For keys see https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes
BUTTONS = {
    # Left (VK_LBUTTON = 1)
    -1: 1,
    'l': 1,
    'L': 1,
    # Middle (VK_MBUTTON = 4)
    0: 4,
    'm': 4,
    'M': 4,
    # Right ('RBUTTON = 2)': 1: 2,,
    'r': 2,
    'R': 2,
}

KEY_MAP = {
    'LMB': 0x01,
    'RMB': 0x02,
    'CANCEL': 0x03,
    'MMB': 0x04,
    '\r': 0x08,
    '\t': 0x09,
    'CLEAR': 0x0C,
    '\n': 0x0D,
    'SHIFT': 0x10,
    'CTRL': 0x11,
    'ALT': 0x12,
    'PAUSE': 0x13,
    'CAPSLOCK': 0x14,
    'ESC': 0x1B,
    'PAGEUP': 0x21,
    'PAGEDOWN': 0x22,
    'END': 0x23,
    'HOME': 0x24,
    'LEFT': 0x25,
    'UP': 0x26,
    'RIGHT': 0x27,
    'DOWN': 0x28,
    'SELECT': 0x29,
    'PRINT': 0x2A,
    'EXEC': 0x2B,
    'PRSCR': 0x2C,
    'INS': 0x2D,
    'DEL': 0x2E,
    'HELP': 0x2F,
    'SUPER': 0x5B,
    'F1': 0x70,
    'F2': 0x71,
    'F3': 0x72,
    'F4': 0x73,
    'F5': 0x74,
    'F6': 0x75,
    'F7': 0x76,
    'F8': 0x77,
    'F9': 0x78,
    'F10': 0x79,
    'F11': 0x7A,
    'F12': 0x7B,
    'F13': 0x7C,
    'F14': 0x7D,
    'F15': 0x7E,
    'F16': 0x7F,
    'F17': 0x80,
    'F18': 0x81,
    'F19': 0x82,
    'F20': 0x83,
    'F21': 0x84,
    'F22': 0x85,
    'F23': 0x86,
    'F24': 0x87,
    'NUMLOCK': 0x90,
    'SCROLLLOCK': 0x91,
    'LSHIFT': 0xA0,
    'RSHIFT': 0xA1,
    'LCTRL': 0xA2,
    'RCTRL': 0xA3,
    'LALT': 0xA4,
    'RALT': 0xA5,
    'MUTE': 0xAD,
    'VOLDOWN': 0xAE,
    'VOLUP': 0xAF,
    'MEDIANEXT': 0xB0,
    'MEDIAPREV': 0xB1,
    'MEDIASTOP': 0xB2,
    'MEDIAPLAYPAUSE': 0xB3,
}

def _key_to_vk(key):
    key = key.upper()
    try:
        return KEY_MAP[key]
    except KeyError:
        # TODO VkKeyScanExA
        return ord(key)


BUTTON_TO_EVENTS = {
    1: (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    2: (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    4: (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

def _parse_button(n):
    try:
        return BUTTONS[n]
    except KeyError:
        raise ValueError('Invalid button given') from None


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


def wait_mouse(which):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getasynckeystate
    SHORT GetAsyncKeyState(
        int vKey
    );
    """
    # 1 for left, 2 for right
    while True:  # wait down
        time.sleep(0.01)
        if ctypes.windll.user32.GetAsyncKeyState(which):
            break

    while True:  # wait release
        time.sleep(0.01)
        if not ctypes.windll.user32.GetAsyncKeyState(which):
            break

    return get_mouse()


def wait_key(before=ctypes.create_string_buffer(256), after=ctypes.create_string_buffer(256)):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeyboardstate
    BOOL GetKeyboardState(
        PBYTE lpKeyState
    );
    """
    # get the current keyboard state
    ctypes.windll.user32.GetKeyState(0)  # needed for some reason
    ctypes.windll.user32.GetKeyboardState(before)
    for i in range(256):
        before[i] = int((before[i][0] & 0x80) != 0)

    while True:  # get the new keyboard state...
        time.sleep(0.05)
        ctypes.windll.user32.GetKeyState(0)  # needed for some reason
        ctypes.windll.user32.GetKeyboardState(after)
        for key, (b, a) in enumerate(zip(before, after)):
            b = b[0]
            a = int((a[0] & 0x80) != 0)
            if b != a:  # ...until we find a difference,
                # then wait until the pressed key is released
                while True:
                    time.sleep(0.05)
                    if not ctypes.windll.user32.GetAsyncKeyState(key):
                        return key


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


def is_down(vk):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getkeystate
    SHORT GetKeyState(
        int nVirtKey
    );
    """
    return (ctypes.windll.user32.GetKeyState(vk) & 0x80) != 0


def _press(key, down=None):
    """
    https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-sendinput
    UINT SendInput(
        UINT    cInputs,
        LPINPUT pInputs,
        int     cbSize
    );
    """
    if down is None:
        _press(key, True)
        _press(key, False)
        return

    count = ctypes.c_uint(1)
    inputs = INPUT(type=INPUT_KEYBOARD, value=INPUTUNION(ki=KEYBDINPUT(
        wVk=_key_to_vk(key),
        wScan=0,
        dwFlags=0 if down else KEYEVENTF_KEYUP,
        time=0,
        dwExtraInfo=None
    )))
    ctypes.windll.user32.SendInput(count, ctypes.byref(inputs), ctypes.sizeof(inputs))


def press(*keys):
    # TODO we can actually send an array to sendinput here
    for key in keys:
        _press(key)


@contextmanager
def hold(*keys):
    for key in keys:
        _press(key, down=True)
    try:
        yield
    finally:
        for key in keys:
            _press(key, down=False)


def click(*args):
    # TODO move mouse with the call directly
    argc = len(args)
    assert argc < 4, 'Invalid number of arguments'
    if argc & 2:
        move(args[0], args[1])

    button = _parse_button(args[-1]) if argc & 1 else 1
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
    buffer = s.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(buffer) + 2)
    cstring = GlobalLock(handle)
    ctypes.memmove(cstring, buffer, len(buffer))
    GlobalUnlock(handle)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard()
