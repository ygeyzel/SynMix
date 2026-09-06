from enum import Enum
from typing import NamedTuple

from frozendict import frozendict

MIDI_MIN_VALUE = 0
MIDI_MAX_VALUE = 127

MIDI_BUTTEN_CLICK = 127
MIDI_BUTTEN_RELEASE = 0

# A scroller value up to this decreases, above it increases
MAX_DEC_SCROLL_VALUE = 63
# The values encoding a single step, at the outer end of each direction's range
INC_SCROLL_STEP_VALUE = MIDI_MAX_VALUE
DEC_SCROLL_STEP_VALUE = MIDI_MIN_VALUE

MAX_PITCH = 8191
MIN_PITCH = -8192


class MidiEventType(Enum):
    NOTE_ON = "note_on"
    CONTROL_CHANGE = "control_change"
    PITCH = "pitchwheel"


class ScrollMode(Enum):
    """How the value of a scroller event is read."""

    # The value only tells the direction, every event is a single step
    DIR_ONLY = "dir_only"
    # The value also carries the magnitude of the step
    ACCUMULATE = "accumulate"


class ScrollStep(NamedTuple):
    is_increase: bool
    steps: int


def decode_scroll(value: int, scroll_mode: ScrollMode) -> ScrollStep:
    """
    Read a scroller event as a direction and a number of steps.

    Under ACCUMULATE the step count grows the further the value is from the outer
    end of its direction: 127 is one step up, 126 two, and 0 is one step down, 1 two.
    """
    is_increase = value > MAX_DEC_SCROLL_VALUE
    if scroll_mode is ScrollMode.ACCUMULATE:
        outer_end = INC_SCROLL_STEP_VALUE if is_increase else DEC_SCROLL_STEP_VALUE
        steps = abs(value - outer_end) + 1
    else:
        steps = 1

    return ScrollStep(is_increase, steps)


class MidiEventDesricptors(NamedTuple):
    SELECTOR_FIELD: str
    VALUE_FIELD: str


MIN_CHANNEL = 0
MAX_CHANNEL = 15


class MidiGetter(NamedTuple):
    event_type: MidiEventType
    selector_value: int
    channel: int | None = None  # None matches events on any channel


MIDI_EVENT_DESCRIPTORS = frozendict(
    {
        MidiEventType.NOTE_ON: MidiEventDesricptors("note", "velocity"),
        MidiEventType.CONTROL_CHANGE: MidiEventDesricptors("control", "value"),
        MidiEventType.PITCH: MidiEventDesricptors("channel", "pitch"),
    }
)


def get_midi_event_descriptor(event_type: MidiEventType) -> MidiEventDesricptors:
    return MIDI_EVENT_DESCRIPTORS[event_type]
