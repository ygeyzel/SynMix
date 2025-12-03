from enum import Enum
from typing import NamedTuple

from frozendict import frozendict

MIDI_INC_VALUE = 65
MIDI_DEC_VALUE = 63

MIDI_MIN_VALUE = 0
MIDI_MAX_VALUE = 127

MIDI_BUTTEN_CLICK = 127
MIDI_BUTTEN_RELEASE = 0

MAX_PITCH = 8191
MIN_PITCH = -8192


class MidiEventType(Enum):
    NOTE_ON = "note_on"
    CONTROL_CHANGE = "control_change"
    PITCH = "pitchwheel"


class MidiEventDesricptors(NamedTuple):
    SELECTOR_FIELD: str
    VALUE_FIELD: str


class MidiGetter(NamedTuple):
    event_type: MidiEventType
    selector_value: int


MIDI_EVENT_DESCRIPTORS = frozendict(
    {
        MidiEventType.NOTE_ON: MidiEventDesricptors("note", "velocity"),
        MidiEventType.CONTROL_CHANGE: MidiEventDesricptors("control", "value"),
        MidiEventType.PITCH: MidiEventDesricptors("channel", "pitch"),
    }
)


def get_midi_event_descriptor(event_type: MidiEventType) -> MidiEventDesricptors:
    return MIDI_EVENT_DESCRIPTORS[event_type]
