from enum import Enum
from typing import NamedTuple

from frozendict import frozendict


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
