from enum import Enum
from inputs.midi import MidiEventType, MidiGetter


class Button(Enum):
    LEFT_WHEEL = MidiGetter(MidiEventType.CONTROL_CHANGE, 36)
    RIGHT_WHEEL = MidiGetter(MidiEventType.CONTROL_CHANGE, 37)
    LEFT_HIGH = MidiGetter(MidiEventType.CONTROL_CHANGE, 53)
    LEFT_MID = MidiGetter(MidiEventType.CONTROL_CHANGE, 54)
    LEFT_LOW = MidiGetter(MidiEventType.CONTROL_CHANGE, 55)
    RIGHT_HIGH = MidiGetter(MidiEventType.CONTROL_CHANGE, 59)
    RIGHT_MID = MidiGetter(MidiEventType.CONTROL_CHANGE, 60)
    RIGHT_LOW = MidiGetter(MidiEventType.CONTROL_CHANGE, 61)

