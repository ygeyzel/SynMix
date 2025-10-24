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

    RIGHT_LOAD = MidiGetter(MidiEventType.NOTE_ON, 13)
    LEFT_LOAD = MidiGetter(MidiEventType.NOTE_ON, 27)
    SCROLL = MidiGetter(MidiEventType.CONTROL_CHANGE, 31)
    SCROLL_CLICK = MidiGetter(MidiEventType.NOTE_ON, 31)

    LEFT_PITCH = MidiGetter(MidiEventType.PITCH, 0)
    RIGHT_PITCH = MidiGetter(MidiEventType.PITCH, 1)

    LEFT_LENGHT = MidiGetter(MidiEventType.CONTROL_CHANGE, 32)
    LEFT_DRY_WET = MidiGetter(MidiEventType.CONTROL_CHANGE, 33)
    LEFT_GAIN = MidiGetter(MidiEventType.CONTROL_CHANGE, 51)
    LEFT_AMOUNT = MidiGetter(MidiEventType.CONTROL_CHANGE, 52)

    RIGHT_LENGHT = MidiGetter(MidiEventType.CONTROL_CHANGE, 57)
    RIGHT_DRY_WET = MidiGetter(MidiEventType.CONTROL_CHANGE, 58)
    RIGHT_GAIN = MidiGetter(MidiEventType.CONTROL_CHANGE, 34)
    RIGHT_AMOUNT = MidiGetter(MidiEventType.CONTROL_CHANGE, 35)

    LEFT_VOLUME = MidiGetter(MidiEventType.CONTROL_CHANGE, 56)
    RIGHT_VOLUME = MidiGetter(MidiEventType.CONTROL_CHANGE, 62)
    CROSSFADER = MidiGetter(MidiEventType.CONTROL_CHANGE, 49)
    CUEMIX = MidiGetter(MidiEventType.CONTROL_CHANGE, 50)

    LEFT_CUE_1 = MidiGetter(MidiEventType.NOTE_ON, 9)
    LEFT_CUE_2 = MidiGetter(MidiEventType.NOTE_ON, 10)
    LEFT_CUE_3 = MidiGetter(MidiEventType.NOTE_ON, 11)
    LEFT_CUE_4 = MidiGetter(MidiEventType.NOTE_ON, 12)

    RIGHT_CUE_1 = MidiGetter(MidiEventType.NOTE_ON, 23)
    RIGHT_CUE_2 = MidiGetter(MidiEventType.NOTE_ON, 24)
    RIGHT_CUE_3 = MidiGetter(MidiEventType.NOTE_ON, 25)
    RIGHT_CUE_4 = MidiGetter(MidiEventType.NOTE_ON, 26)

    LEFT_SYNC = MidiGetter(MidiEventType.NOTE_ON, 3)
    LEFT_RECORD = MidiGetter(MidiEventType.NOTE_ON, 4)

    RIGHT_SYNC = MidiGetter(MidiEventType.NOTE_ON, 17)
    RIGHT_RECORD = MidiGetter(MidiEventType.NOTE_ON, 18)

    LEFT_MINUS = MidiGetter(MidiEventType.NOTE_ON, 1)
    LEFT_PLUS = MidiGetter(MidiEventType.NOTE_ON, 2)
    LEFT_SHIFT = MidiGetter(MidiEventType.NOTE_ON, 42)

    RIGHT_MINUS = MidiGetter(MidiEventType.NOTE_ON, 15)
    RIGHT_PLUS = MidiGetter(MidiEventType.NOTE_ON, 16)
    RIGHT_SHIFT = MidiGetter(MidiEventType.NOTE_ON, 43)

    LEFT_IN = MidiGetter(MidiEventType.NOTE_ON, 5)
    LEFT_OUT = MidiGetter(MidiEventType.NOTE_ON, 6)
    LEFT_FX_SEL = MidiGetter(MidiEventType.NOTE_ON, 7)
    LEFT_FX_ON = MidiGetter(MidiEventType.NOTE_ON, 8)

    RIGHT_IN = MidiGetter(MidiEventType.NOTE_ON, 19)
    RIGHT_OUT = MidiGetter(MidiEventType.NOTE_ON, 20)
    RIGHT_FX_SEL = MidiGetter(MidiEventType.NOTE_ON, 21)
    RIGHT_FX_ON = MidiGetter(MidiEventType.NOTE_ON, 22)
