from enum import Enum

from synmix.inputs.midi import MidiEventType, MidiGetter


class ButtonType(Enum):
    KNOB = "KNOB"
    SCROLLER = "SCROLLER"
    CLICKABLE = "CLICKABLE"


class Button(Enum):
    LEFT_WHEEL = (MidiGetter(MidiEventType.CONTROL_CHANGE, 36), ButtonType.SCROLLER)
    RIGHT_WHEEL = (MidiGetter(MidiEventType.CONTROL_CHANGE, 37), ButtonType.SCROLLER)

    LEFT_HIGH = (MidiGetter(MidiEventType.CONTROL_CHANGE, 53), ButtonType.KNOB)
    LEFT_MID = (MidiGetter(MidiEventType.CONTROL_CHANGE, 54), ButtonType.KNOB)
    LEFT_LOW = (MidiGetter(MidiEventType.CONTROL_CHANGE, 55), ButtonType.KNOB)

    RIGHT_HIGH = (MidiGetter(MidiEventType.CONTROL_CHANGE, 59), ButtonType.KNOB)
    RIGHT_MID = (MidiGetter(MidiEventType.CONTROL_CHANGE, 60), ButtonType.KNOB)
    RIGHT_LOW = (MidiGetter(MidiEventType.CONTROL_CHANGE, 61), ButtonType.KNOB)

    RIGHT_LOAD = (MidiGetter(MidiEventType.NOTE_ON, 13), ButtonType.CLICKABLE)
    LEFT_LOAD = (MidiGetter(MidiEventType.NOTE_ON, 27), ButtonType.CLICKABLE)
    SCROLL = (MidiGetter(MidiEventType.CONTROL_CHANGE, 31), ButtonType.SCROLLER)
    SCROLL_CLICK = (MidiGetter(MidiEventType.NOTE_ON, 31), ButtonType.CLICKABLE)

    LEFT_PITCH = (MidiGetter(MidiEventType.PITCH, 0), ButtonType.KNOB)
    RIGHT_PITCH = (MidiGetter(MidiEventType.PITCH, 1), ButtonType.KNOB)

    LEFT_LENGTH = (MidiGetter(MidiEventType.CONTROL_CHANGE, 32), ButtonType.SCROLLER)
    LEFT_DRY_WET = (MidiGetter(MidiEventType.CONTROL_CHANGE, 33), ButtonType.SCROLLER)
    LEFT_GAIN = (MidiGetter(MidiEventType.CONTROL_CHANGE, 51), ButtonType.KNOB)
    LEFT_AMOUNT = (MidiGetter(MidiEventType.CONTROL_CHANGE, 52), ButtonType.KNOB)

    RIGHT_LENGTH = (MidiGetter(MidiEventType.CONTROL_CHANGE, 34), ButtonType.SCROLLER)
    RIGHT_DRY_WET = (MidiGetter(MidiEventType.CONTROL_CHANGE, 35), ButtonType.SCROLLER)
    RIGHT_GAIN = (MidiGetter(MidiEventType.CONTROL_CHANGE, 57), ButtonType.KNOB)
    RIGHT_AMOUNT = (MidiGetter(MidiEventType.CONTROL_CHANGE, 58), ButtonType.KNOB)

    LEFT_VOLUME = (MidiGetter(MidiEventType.CONTROL_CHANGE, 56), ButtonType.KNOB)
    RIGHT_VOLUME = (MidiGetter(MidiEventType.CONTROL_CHANGE, 62), ButtonType.KNOB)
    CROSSFADER = (MidiGetter(MidiEventType.CONTROL_CHANGE, 49), ButtonType.KNOB)
    CUEMIX = (MidiGetter(MidiEventType.CONTROL_CHANGE, 50), ButtonType.KNOB)

    LEFT_CUE_1 = (MidiGetter(MidiEventType.NOTE_ON, 9), ButtonType.CLICKABLE)
    LEFT_CUE_2 = (MidiGetter(MidiEventType.NOTE_ON, 10), ButtonType.CLICKABLE)
    LEFT_CUE_3 = (MidiGetter(MidiEventType.NOTE_ON, 11), ButtonType.CLICKABLE)
    LEFT_CUE_4 = (MidiGetter(MidiEventType.NOTE_ON, 12), ButtonType.CLICKABLE)

    RIGHT_CUE_1 = (MidiGetter(MidiEventType.NOTE_ON, 23), ButtonType.CLICKABLE)
    RIGHT_CUE_2 = (MidiGetter(MidiEventType.NOTE_ON, 24), ButtonType.CLICKABLE)
    RIGHT_CUE_3 = (MidiGetter(MidiEventType.NOTE_ON, 25), ButtonType.CLICKABLE)
    RIGHT_CUE_4 = (MidiGetter(MidiEventType.NOTE_ON, 26), ButtonType.CLICKABLE)

    LEFT_SYNC = (MidiGetter(MidiEventType.NOTE_ON, 3), ButtonType.CLICKABLE)
    LEFT_RECORD = (MidiGetter(MidiEventType.NOTE_ON, 4), ButtonType.CLICKABLE)

    RIGHT_SYNC = (MidiGetter(MidiEventType.NOTE_ON, 17), ButtonType.CLICKABLE)
    RIGHT_RECORD = (MidiGetter(MidiEventType.NOTE_ON, 18), ButtonType.CLICKABLE)

    LEFT_MINUS = (MidiGetter(MidiEventType.NOTE_ON, 1), ButtonType.CLICKABLE)
    LEFT_PLUS = (MidiGetter(MidiEventType.NOTE_ON, 2), ButtonType.CLICKABLE)
    LEFT_SHIFT = (MidiGetter(MidiEventType.NOTE_ON, 42), ButtonType.CLICKABLE)

    RIGHT_MINUS = (MidiGetter(MidiEventType.NOTE_ON, 15), ButtonType.CLICKABLE)
    RIGHT_PLUS = (MidiGetter(MidiEventType.NOTE_ON, 16), ButtonType.CLICKABLE)
    RIGHT_SHIFT = (MidiGetter(MidiEventType.NOTE_ON, 43), ButtonType.CLICKABLE)

    LEFT_IN = (MidiGetter(MidiEventType.NOTE_ON, 5), ButtonType.CLICKABLE)
    LEFT_OUT = (MidiGetter(MidiEventType.NOTE_ON, 6), ButtonType.CLICKABLE)
    LEFT_FX_SEL = (MidiGetter(MidiEventType.NOTE_ON, 7), ButtonType.CLICKABLE)
    LEFT_FX_ON = (MidiGetter(MidiEventType.NOTE_ON, 8), ButtonType.CLICKABLE)

    RIGHT_IN = (MidiGetter(MidiEventType.NOTE_ON, 19), ButtonType.CLICKABLE)
    RIGHT_OUT = (MidiGetter(MidiEventType.NOTE_ON, 20), ButtonType.CLICKABLE)
    RIGHT_FX_SEL = (MidiGetter(MidiEventType.NOTE_ON, 21), ButtonType.CLICKABLE)
    RIGHT_FX_ON = (MidiGetter(MidiEventType.NOTE_ON, 22), ButtonType.CLICKABLE)

    @property
    def midi_getter(self) -> MidiGetter:
        return self.value[0]

    @property
    def button_type(self) -> ButtonType:
        return self.value[1]
