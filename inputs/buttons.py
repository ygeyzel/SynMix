from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from pyglet.window import key


# currently a placeholder for MIDI input handling
class MidiGetter:
    pass


@dataclass
class ButtonGetter:
    keyboard_keys: Tuple[int, ...]
    midi: MidiGetter


class Button(Enum):
    LEFT_WHEEL = ButtonGetter((key.LEFT, key.RIGHT), MidiGetter())
    RIGHT_WHEEL = ButtonGetter((key.UP, key.DOWN), MidiGetter())
    RANGED_PLACEHOLDER = ButtonGetter((key.Q, key.A), MidiGetter())
    BUTTON_1 = ButtonGetter((key._1, key._2), MidiGetter())
    BUTTON_2 = ButtonGetter((key._3, key._4), MidiGetter())
    BUTTON_3 = ButtonGetter((key._5, key._6), MidiGetter())
    BUTTON_4 = ButtonGetter((key._7, key._8), MidiGetter())
    BUTTON_5 = ButtonGetter((key._9, key._0), MidiGetter())

