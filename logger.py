import itertools

import Xlib
import Xlib.XK
import Xlib.display
import Xlib.ext
import Xlib.ext.record
import Xlib.protocol


class Logger:
    def __init__(self):
        self.local_dpy = Xlib.display.Display()
        self.record_dpy = Xlib.display.Display()
        if 'RECORD' not in self.record_dpy.extensions:
            raise ValueError('xwindows does not have the RECORD extension')

        self._key_cb = None
        self._mouse_cb = None

        self._context = None
        self._field = Xlib.protocol.rq.EventField(None)

        self._mouse_pos = (0, 0)
        self._shift_held = False
        self._caps_held = False
        self._shiftable = {getattr(Xlib.XK, f'XK_{name}')
                           for name in itertools.chain(
            'abcdefghijklmnopqrstuvwxyz0123456789',
            ('minus', 'equal', 'bracketleft', 'bracketright', 'semicolon',
             'backslash', 'apostrophe', 'comma', 'period', 'slash', 'grave')
        )}

        self._shift_keys = (
            Xlib.XK.XK_Shift_L, Xlib.XK.XK_Shift_R, Xlib.XK.XK_Shift_Lock
        )

    def keyboard(self, func):
        """
        Decorator to be attached to the function that
        will receive keyboard events when they occur:

        >>> log = Logger(...)
        >>>
        >>> @log.keyboard
        ... def on_kbd(event):
        ...     if event.down:
        ...         pass  # Some code...
        ...
        """
        self._key_cb = func
        return func

    def mouse(self, func):
        """
        Decorator to be attached to the function that
        will receive keyboard events when they occur:

        >>> log = Logger(...)
        >>>
        >>> @log.mouse
        ... def on_mouse(event):
        ...     if event.up:
        ...         pass  # Some code...
        ...
        """
        self._mouse_cb = func
        return func

    def run(self):
        """
        Creates a new record context to enable logging.
        """
        null = (0, 0)
        big_null = (0, 0, 0, 0)
        self._context = self.record_dpy.record_create_context(
            0,
            [Xlib.ext.record.AllClients],
            [{
                'core_requests': null,
                'core_replies': null,
                'ext_requests': big_null,
                'ext_replies': big_null,
                'delivered_events': null,
                'device_events': (Xlib.X.KeyPress, Xlib.X.MotionNotify),
                'errors': null,
                'client_started': 0,
                'client_died': 0,
            }])

        try:
            self.record_dpy.record_enable_context(
                self._context, self._process_events)
        except KeyboardInterrupt:
            pass
        finally:
            self.record_dpy.record_free_context(self._context)

    def stop(self):
        """
        Cleanly stops running the logger.
        """
        if self._context:
            self.local_dpy.record_disable_context(self._context)
            self.local_dpy.flush()
            self._context = None

    def _process_events(self, reply):
        if (reply.category != Xlib.ext.record.FromServer
            or reply.client_swapped
            or not reply.data
                or reply.data[0] < 2):
            return

        data = reply.data
        while data:
            event, data = self._field.parse_binary_value(
                data, self.record_dpy.display, None, None
            )

            if self._key_cb:
                if event.type == Xlib.X.KeyPress:
                    self._key_cb(self._create_key_press_event(event))
                elif event.type == Xlib.X.KeyRelease:
                    self._key_cb(self._create_key_release_event(event))

            if self._mouse_cb:
                if event.type == Xlib.X.ButtonPress:
                    self._mouse_cb(self._create_button_press_event(event))
                elif event.type == Xlib.X.ButtonRelease:
                    self._mouse_cb(self._create_button_release_event(event))
                elif event.type == Xlib.X.MotionNotify:
                    self._mouse_cb(self._create_mouse_move_event(event))

    def _create_key_press_event(self, event):
        keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        if (self._shift_held or self._caps_held) and keysym in self._shiftable:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
        elif keysym in self._shift_keys:
            self._shift_held = True
        elif keysym == Xlib.XK.XK_Caps_Lock:
            self._caps_held = not self._caps_held

        return KeyEvent(keysym, True, self._shift_held, self._caps_held)

    def _create_key_release_event(self, event):
        keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        if (self._shift_held or self._caps_held) and keysym in self._shiftable:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
        elif keysym in self._shift_keys:
            self._shift_held = False

        return KeyEvent(keysym, False, self._shift_held, self._caps_held)

    def _create_button_press_event(self, event):
        return MouseEvent(event.detail, True, self._mouse_pos, False)

    def _create_button_release_event(self, event):
        return MouseEvent(event.detail, False, self._mouse_pos, False)

    def _create_mouse_move_event(self, event):
        self._mouse_pos = (event.root_x, event.root_y)
        return MouseEvent(0, None, self._mouse_pos, True)

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, *_):
        self.stop()


class KeyEvent:
    """
    Represents a key event.

    Attributes:
        key   : The key code from Xlib.XK.XK_...
        down  : True if the key is being held down.
        up    : True if the key is not being held down.
        shift : True if the shift key is held down.
        caps  : True if the caps lock is on.
    """
    _key_to_name = {
        getattr(Xlib.XK, name): name[3:]
        for name in dir(Xlib.XK)
        if name.startswith('XK_')
    }

    def __init__(self, key, down, shift, caps):
        self.key = key
        self.down = down
        self.up = not down
        self.shift = shift
        self.caps = caps

    @property
    def name(self):
        """
        The name for this key code.
        """
        return self._lookup_keysym(self.key)

    @property
    def ord(self):
        """
        The ASCII value for this key code.
        """
        return self._keysym_to_ascii(self.key)

    @classmethod
    def _lookup_keysym(cls, key):
        # Xlib.XK.keysym_to_string is not the inverse of string_to_keysym
        # as it doesn't handle non-printable characters.
        return cls._key_to_name.get(key, f'[{key}]')

    @classmethod
    def _keysym_to_ascii(cls, keysym):
        value = Xlib.XK.string_to_keysym(cls._lookup_keysym(keysym))
        print(keysym, value)
        return value if value < 256 else 0


class MouseEvent:
    """
    Represents a mouse event.

    Attributes:
        left   : True if the left button changed.
        right  : True if the right button changed.
        middle : True if the middle button changed.
        wheel  : +1 if the wheel scrolled up, -1 scrolled down, 0 otherwise.
        other  : The original button code.
        down   : Whether the button in question was pressed down.
        up     : Whether the button in question was released.
        x      : The x coordinate of the mouse in screen.
        y      : The y coordinate of the mouse in screen.
        pos    : The position tuple as (x, y).
        move   : True if the mouse moved.
    """
    def __init__(self, other, down, pos, move):
        self.left = other == Xlib.X.Button1
        self.right = other == Xlib.X.Button3
        self.middle = other == Xlib.X.Button2
        if other == Xlib.X.Button4:
            self.wheel = 1
        elif other == Xlib.X.Button5:
            self.wheel = -1
        else:
            self.wheel = 0

        self.other = other
        self.down = down
        self.up = not down
        self.x, self.y = pos
        self.pos = pos
        self.move = move
