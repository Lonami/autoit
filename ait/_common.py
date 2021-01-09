from collections import namedtuple
from enum import Enum

Position = namedtuple('Position', 'x y')
Color = namedtuple('Color', 'r g b')

class MB(Enum):
    L = -1
    M = 0
    R = +1

    @classmethod
    def parse(cls, value):
        if isinstance(value, (int, float)):
            if value < 0:
                return MB.L
            elif value > 0:
                return MB.R
            else:
                return MB.M

        elif isinstance(value, str):
            value = value.upper()
            if value in ('L', 'LMB'):
                return MB.L
            elif value in ('R', 'RMB'):
                return MB.R
            elif value in ('M', 'MMB'):
                return MB.M

        return ValueError('Invalid mouse button {!r}'.format(value))
