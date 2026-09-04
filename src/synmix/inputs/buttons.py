from enum import Enum
from typing import NamedTuple

from synmix.inputs.midi import MidiGetter


class ButtonType(Enum):
    KNOB = "KNOB"
    SCROLLER = "SCROLLER"
    CLICKABLE = "CLICKABLE"


class Button(NamedTuple):
    """A single control on a MIDI device, as described by a midi config file."""

    midi_getter: MidiGetter
    button_type: ButtonType
    index: int
    label: str | None = None

    @property
    def section(self) -> str:
        return SECTION_BY_BUTTON_TYPE[self.button_type]

    def __repr__(self) -> str:
        label = f"{self.label} " if self.label else ""
        return f"Button({label}{self.section}[{self.index}])"


BUTTON_TYPE_BY_SECTION = {
    "knobs": ButtonType.KNOB,
    "scrollers": ButtonType.SCROLLER,
    "clickables": ButtonType.CLICKABLE,
}

SECTION_BY_BUTTON_TYPE = {
    button_type: section for section, button_type in BUTTON_TYPE_BY_SECTION.items()
}
