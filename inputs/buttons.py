from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from pyglet.window import key


# currently a placeholder for MIDI input handling
class MidiGetter:
    pass


@dataclass
class ButtonGetter:
    keyboard_keys: Tuple[key]
    midi: MidiGetter


class Button(Enum):
    LEFT_WHEEL = ButtonGetter((key.LEFT, key.RIGHT), MidiGetter())
    RIGHT_WHEEL = ButtonGetter((key.UP, key.DOWN), MidiGetter())
    RANGED_PLACEHOLDER = ButtonGetter((key.Q, key.A), MidiGetter())

