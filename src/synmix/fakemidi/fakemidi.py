import json
import platform
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial, reduce
from pathlib import Path
from typing import NamedTuple

import mido
from pyglet.window import key as pyglet_key

from synmix.inputs.buttons import BUTTON_TYPE_BY_SECTION, Button, ButtonType
from synmix.inputs.midi import (
    MAX_PITCH,
    MIDI_MAX_VALUE,
    MIDI_MIN_VALUE,
    MIN_PITCH,
    MidiEventType,
    get_midi_event_descriptor,
)
from synmix.inputs.midi_config import MidiConfig

PITCH_STEP_FACTOR = 64

FAKE_MIDI_OUTPUT_NAME = "Fake MIDI Controller"

FAKE_MIDI_CHANNEL = 0
FAKE_INC_SCROLL_VALUE = 65
FAKE_DEC_SCROLL_VALUE = 63
# Mirrors the real devices, which put their pitch knobs here, so that params
# declaring is_pitch keep their full range under the fake controller
FAKE_PITCH_KNOB_INDICES = (6, 7)
# The same positions the real devices bind their functions to, which is what the
# documented keyboard mapping expects: F1/F2/F5 for scenes, F3/F4 for time offset
# and F10/F11 or HOME/END for speed
FAKE_MIDI_FUNCTIONS = {
    "next_scene": [["clickables", 0]],
    "previous_scene": [["clickables", 1]],
    "random_scene": [["clickables", 2]],
    "time_offset": [["scrollers", 2]],
    "decrease_speed": [["clickables", 15], ["clickables", 18]],
    "increase_speed": [["clickables", 16], ["clickables", 19]],
}


class KeyMessageParams(NamedTuple):
    pressed_params: dict
    released_params: dict | None


class ButtonInterface(ABC):
    def __init__(self, button: Button, midi_config: MidiConfig) -> None:
        midi_getter = button.midi_getter
        self.midi_config = midi_config
        self.event_type = midi_getter.event_type

        event_descriptor = get_midi_event_descriptor(self.event_type)
        self.selector_field = event_descriptor.SELECTOR_FIELD
        self.value_field = event_descriptor.VALUE_FIELD
        self.selector_value = midi_getter.selector_value
        self.channel = midi_getter.channel

    def _generate_base_message_dict(self) -> dict:
        message_dict = {
            "type": self.event_type.value,
            self.selector_field: self.selector_value,
        }

        # A button bound to a specific channel only matches messages on that channel
        if self.channel is not None:
            message_dict["channel"] = self.channel

        return message_dict

    @abstractmethod
    def generate_messages(self, *args, **kwargs) -> list[mido.Message]:
        pass

    @property
    @abstractmethod
    def key_messages_params(self) -> list[KeyMessageParams]:
        pass

    def keys_messages_methods(self) -> list[tuple[Callable, Callable | None]]:
        return [
            (
                partial(self.generate_messages, **params.pressed_params),
                partial(self.generate_messages, **params.released_params)
                if params.released_params
                else None,
            )
            for params in self.key_messages_params
        ]


class KnobInterface(ButtonInterface):
    def __init__(self, button: Button, midi_config: MidiConfig) -> None:
        super().__init__(button, midi_config)
        event_type = button.midi_getter.event_type
        if event_type is MidiEventType.PITCH:
            self.current_value = 0
            self.min_value = MIN_PITCH
            self.max_value = MAX_PITCH
            self.step_factor = PITCH_STEP_FACTOR
        else:
            self.current_value = 64
            self.min_value = MIDI_MIN_VALUE
            self.max_value = MIDI_MAX_VALUE
            self.step_factor = 1

    def _step_value(self, step: int) -> None:
        new_value = self.current_value + step
        self.current_value = max(self.min_value, min(self.max_value, new_value))

    def generate_messages(
        self, step: int, is_inc_dir: bool, **kwargs
    ) -> list[mido.Message]:
        message_dict = self._generate_base_message_dict()

        dir_factor = 1 if is_inc_dir else -1
        self._step_value(step * self.step_factor * dir_factor)
        message_dict[self.value_field] = self.current_value

        return [mido.Message(**message_dict)]

    @property
    def key_messages_params(self) -> list[KeyMessageParams]:
        return [
            KeyMessageParams(pressed_params={"is_inc_dir": True}, released_params=None),
            KeyMessageParams(
                pressed_params={"is_inc_dir": False}, released_params=None
            ),
        ]


class ScrollerInterface(ButtonInterface):
    def generate_messages(
        self, is_inc_dir: bool, repeats: int, **kwargs
    ) -> list[mido.Message]:
        message_dict = self._generate_base_message_dict()
        message_dict[self.value_field] = (
            self.midi_config.inc_scroll_value
            if is_inc_dir
            else self.midi_config.dec_scroll_value
        )
        return [mido.Message(**message_dict)] * repeats

    @property
    def key_messages_params(self) -> list[KeyMessageParams]:
        return [
            KeyMessageParams(pressed_params={"is_inc_dir": True}, released_params=None),
            KeyMessageParams(
                pressed_params={"is_inc_dir": False}, released_params=None
            ),
        ]


class ClickableInterface(ButtonInterface):
    def __init__(self, button: Button, midi_config: MidiConfig) -> None:
        super().__init__(button, midi_config)
        self.is_on = False

    def generate_messages(self, is_on, **kwargs) -> list[mido.Message]:
        if is_on == self.is_on:
            return []

        message_dict = self._generate_base_message_dict()
        message_dict[self.value_field] = MIDI_MAX_VALUE if is_on else MIDI_MIN_VALUE
        self.is_on = is_on

        return [mido.Message(**message_dict)]

    @property
    def key_messages_params(self) -> list[KeyMessageParams]:
        return [
            KeyMessageParams(
                pressed_params={"is_on": True}, released_params={"is_on": False}
            ),
        ]


INTERFACE_BY_BUTTON_TYPE: dict[ButtonType, type[ButtonInterface]] = {
    ButtonType.KNOB: KnobInterface,
    ButtonType.SCROLLER: ScrollerInterface,
    ButtonType.CLICKABLE: ClickableInterface,
}


def interface_factory(button: Button, midi_config: MidiConfig) -> ButtonInterface:
    interface_cls = INTERFACE_BY_BUTTON_TYPE.get(button.button_type)
    if interface_cls is None:
        raise ValueError(
            f"No interface registered for button type {button.button_type}."
        )
    return interface_cls(button, midi_config)


def get_key_code(key_name: str) -> int:
    return getattr(pyglet_key, key_name)


def load_key_map_data(file_path: Path) -> dict:
    """
    Buttons are addressed positionally, matching the midi config sections.
    Knobs and scrollers take two keys, clickables a single one, and an entry
    may be null to leave that button unmapped.

    Example JSON structure:
    {
        "knobs": [["key1", "key2"], null, ...],
        "scrollers": [["key3", "key4"], ...],
        "clickables": ["key5", ...]
    }
    """
    with file_path.open() as f:
        return json.load(f)


def generate_midi_config(key_map_data: dict) -> MidiConfig:
    """
    Build the fake controller's own device mapping, sized to the key map.

    The fake controller is not tied to any physical device, so it invents
    unused event selectors for each button rather than borrowing a real one.
    """
    sections = {}
    control_value = 0

    for section in BUTTON_TYPE_BY_SECTION:
        entries = []
        for index in range(len(key_map_data.get(section, []))):
            if section == "clickables":
                entries.append(
                    {
                        "event_type": MidiEventType.NOTE_ON.value,
                        "value": index,
                        "channel": FAKE_MIDI_CHANNEL,
                    }
                )
            elif section == "knobs" and index in FAKE_PITCH_KNOB_INDICES:
                # A pitchwheel is selected by its channel, so it takes no 'channel'
                entries.append(
                    {
                        "event_type": MidiEventType.PITCH.value,
                        "value": FAKE_PITCH_KNOB_INDICES.index(index),
                    }
                )
            else:
                entries.append(
                    {
                        "event_type": MidiEventType.CONTROL_CHANGE.value,
                        "value": control_value,
                        "channel": FAKE_MIDI_CHANNEL,
                    }
                )
                control_value += 1

        sections[section] = entries

    functions = {
        func_name: refs
        for func_name, refs in FAKE_MIDI_FUNCTIONS.items()
        if all(index < len(sections[section]) for section, index in refs)
    }

    return MidiConfig(
        FAKE_MIDI_OUTPUT_NAME,
        {
            "name": FAKE_MIDI_OUTPUT_NAME,
            "inc_scroll_value": FAKE_INC_SCROLL_VALUE,
            "dec_scroll_value": FAKE_DEC_SCROLL_VALUE,
            **sections,
            "functions": functions,
        },
    )


def load_key_map(key_map_data: dict, midi_config: MidiConfig) -> dict[int, Callable]:
    """
    Bind each mapped key to the methods generating its button's messages.


    Example of returned dictionary:
    {
        <key1>: (<method to generate message for key1 press>, None),
        <key2>: (<method to generate message for key2 press>, None),
        <key3>: (<method to generate message for key3 press>,
                 <method to generate message for key3 release>),
        ...
    }.
    """
    key_map = {}
    for (section, index), keys in get_key_dict(key_map_data).items():
        button = midi_config.get_button(section, index)
        interface = interface_factory(button, midi_config)
        keys_messages_methods = interface.keys_messages_methods()
        if len(keys) != len(keys_messages_methods):
            raise ValueError(
                "Number of keys does not match number of message methods "
                f"for button {button}"
            )

        for key, methods in zip(keys, keys_messages_methods, strict=True):
            key_code = get_key_code(key)
            key_map[key_code] = methods

    return key_map


def get_key_dict(key_map_data: dict) -> dict[tuple[str, int], list[str]]:
    """Map each mapped (section, index) button to its keys."""
    return {
        (section, index): [keys] if isinstance(keys, str) else keys
        for section in BUTTON_TYPE_BY_SECTION
        for index, keys in enumerate(key_map_data.get(section, []))
        if keys
    }


class FakeMidi:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        midi_config: MidiConfig | None = None,
        output_name=FAKE_MIDI_OUTPUT_NAME,
        key_map_file=None,
    ) -> None:
        """Emulate midi_config's device, or the fake controller's own without it."""
        # Only initialize if it's the first time
        if not hasattr(self, "_initialized"):
            # Load default key map file if none provided
            if key_map_file is None:
                from synmix.resource_loader import get_fake_midi_key_map_file

                key_map_file = get_fake_midi_key_map_file()

            self.output_name = output_name
            # Windows doesn't support virtual MIDI ports,
            # so we'll store messages instead
            if platform.system() == "Windows":
                self.output = None
                self.pending_messages = []
            else:
                self.output = mido.open_output(self.output_name, virtual=True)
            self.held_keys = set()
            self.relesed_keys = set()
            self.modifiers = {}
            key_map_data = load_key_map_data(key_map_file)
            self.midi_config = midi_config or generate_midi_config(key_map_data)
            self.key_map = load_key_map(key_map_data, self.midi_config)
            self.key_dict = get_key_dict(key_map_data)
            self._initialized = True

    def handle_keys_input(self) -> None:
        amp = reduce(lambda s, m: s * (2 if m else 1), self.modifiers.values(), 1)

        kwargs = {"step": amp, "is_on": True, "repeats": amp}
        pressed_keys_methods = [
            self.key_map[key][0] for key in self.held_keys if key in self.key_map
        ]
        relesed_keys_methods = [
            self.key_map[key][1]
            for key in self.relesed_keys
            if key in self.key_map and self.key_map[key][1]
        ]

        messages = []
        for methods in (pressed_keys_methods, relesed_keys_methods):
            for method in methods:
                message = method(**kwargs)
                messages += message
            kwargs["is_on"] = False  # For released keys, set is_on to False

        for message in messages:
            if self.output:
                self.output.send(message)
            else:
                # On Windows, store messages for retrieval by input manager
                self.pending_messages.extend(
                    message if isinstance(message, list) else [message]
                )

        for key in self.relesed_keys:
            self.held_keys.remove(key)
        self.relesed_keys.clear()

    def on_key_press(self, key, modifiers) -> None:
        if key in self.held_keys:
            return

        self.held_keys.add(key)
        self.modifiers = modifiers.__dict__

    def on_key_release(self, key) -> None:
        if key in self.held_keys:
            self.relesed_keys.add(key)

        self.modifiers = {}

    def get_pending_messages(self):
        """Get and clear pending MIDI messages (Windows compatibility)."""
        if hasattr(self, "pending_messages"):
            messages = self.pending_messages.copy()
            self.pending_messages.clear()
            return messages
        return []
