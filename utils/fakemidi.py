import json
from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce, partial
from typing import Callable, Dict, List, NamedTuple, Tuple

import mido
from pyglet.window import key as pyglet_key

from inputs.buttons import Button
from inputs.midi import get_midi_event_descriptor, MIDI_DEC_VALUE, MidiEventType, MIDI_INC_VALUE, MIDI_MAX_VALUE, MIDI_MIN_VALUE


MAX_PITCH = 8191
MIN_PITCH = -8192

PITCH_STEP_FACTOR = 64


class KeyMessageParams(NamedTuple):
    pressed_params: dict
    released_params: dict | None


class ButtonInterface(ABC):
    def __init__(self, button: Button):
        self.event_type = button.value.event_type

        event_descriptor = get_midi_event_descriptor(self.event_type)
        self.selector_field = event_descriptor.SELECTOR_FIELD
        self.value_field = event_descriptor.VALUE_FIELD
        self.selector_value = button.value.selector_value

    def _generate_base_message_dict(self) -> dict:
        message_dict = {
            'type': self.event_type.value,
            self.selector_field: self.selector_value,
        }

        return message_dict

    @abstractmethod
    def generate_messages(self, **kwargs) -> List[mido.Message]:
        pass

    @property
    @abstractmethod
    def key_messages_params(self) -> List[KeyMessageParams]:
        pass

    def keys_messages_methods(self) -> List[Tuple[Callable, Callable | None]]:
        return [(partial(self.generate_messages, **params.pressed_params),
                 partial(self.generate_messages, **params.released_params) if params.released_params else None)
                for params in self.key_messages_params]


class StepperInterface(ButtonInterface):
    def __init__(self, button: Button, init_value: int = 64, min_value: int = MIDI_MIN_VALUE, max_value: int = MIDI_MAX_VALUE, step_factor=1):
        super().__init__(button)
        self.current_value = init_value
        self.min_value = min_value
        self.max_value = max_value
        self.step_factor = step_factor

    def _step_value(self, step: int):
        new_value = self.current_value + step
        self.current_value = max(
            self.min_value, min(self.max_value, new_value))

    def generate_messages(self, step: int, is_inc_dir: bool, **kwargs) -> List[mido.Message]:
        message_dict = self._generate_base_message_dict()

        dir_factor = 1 if is_inc_dir else -1
        self._step_value(step * self.step_factor * dir_factor)
        message_dict[self.value_field] = self.current_value

        return [mido.Message(**message_dict)]

    @property
    def key_messages_params(self) -> List[KeyMessageParams]:
        return [
            KeyMessageParams(
                pressed_params={'is_inc_dir': True}, released_params=None),
            KeyMessageParams(
                pressed_params={'is_inc_dir': False}, released_params=None),
        ]


class ScrollerInterface(ButtonInterface):
    def generate_messages(self, is_inc_dir: bool, repeats: int, **kwargs) -> [mido.Message]:
        message_dict = self._generate_base_message_dict()
        message_dict[self.value_field] = MIDI_INC_VALUE if is_inc_dir else MIDI_DEC_VALUE
        return [mido.Message(**message_dict)] * repeats

    @property
    def key_messages_params(self) -> List[KeyMessageParams]:
        return [
            KeyMessageParams(
                pressed_params={'is_inc_dir': True}, released_params=None),
            KeyMessageParams(
                pressed_params={'is_inc_dir': False}, released_params=None),
        ]


class ToggleInterface(ButtonInterface):
    def __init__(self, button: Button):
        super().__init__(button)
        self.is_on = False

    def generate_messages(self, is_on, **kwargs) -> mido.Message | None:
        if is_on == self.is_on:
            return []

        message_dict = self._generate_base_message_dict()
        message_dict[self.value_field] = MIDI_MAX_VALUE if is_on else MIDI_MIN_VALUE
        self.is_on = is_on

        return [mido.Message(**message_dict)]

    @property
    def key_messages_params(self) -> List[KeyMessageParams]:
        return [
            KeyMessageParams(pressed_params={'is_on': True}, released_params={
                             'is_on': False}),
        ]


class InterfaceType(Enum):
    STEPPER = StepperInterface
    SCROLLER = ScrollerInterface
    TOGGLE = ToggleInterface


def interface_factory(button: Button, interface_type: InterfaceType) -> ButtonInterface:
    event_type = button.value.event_type

    match event_type, interface_type:
        case MidiEventType.CONTROL_CHANGE, InterfaceType.STEPPER:
            return StepperInterface(button)

        case MidiEventType.CONTROL_CHANGE, InterfaceType.SCROLLER:
            return ScrollerInterface(button)

        case MidiEventType.NOTE_ON, InterfaceType.TOGGLE:
            return ToggleInterface(button)

        case MidiEventType.PITCH, InterfaceType.STEPPER:
            return StepperInterface(button, init_value=0, min_value=MIN_PITCH, max_value=MAX_PITCH, step_factor=PITCH_STEP_FACTOR)
        case _:
            raise ValueError(
                f"Unsupported combination of event type {event_type} and interface type {interface_type}")


def get_key_code(key_name: str) -> int:
    return getattr(pyglet_key, key_name)


def load_key_map(file_path: str) -> Dict[int, Callable]:
    '''
    Example JSON structure:
    {
        "BUTTON_NAME_0": {
            "interface_type": "STEPPER",
            "keys": ["key1", "key2"]
        },
        "BUTTON_NAME_1": {
            "interface_type": "TOGGLE",
            "keys": ["key3"]
        },
        ...
    }
    Example of returned dictionary:
    {
        <key1>: (<method to generate message for key1 press>, None),
        <key2>: (<method to generate message for key2 press>, None),
        <key3>: (<method to generate message for key3 press>, <method to generate message for key3 release>),
        ...
    }
    '''
    with open(file_path, 'r') as f:
        config = json.load(f)
    key_map = {}
    for button_name, mapping in config.items():
        button = Button[button_name]
        interface_type = InterfaceType[mapping['interface_type']]
        interface = interface_factory(button, interface_type)
        keys_messages_methods = interface.keys_messages_methods()
        if len(mapping['keys']) != len(keys_messages_methods):
            raise ValueError(
                f"Number of keys does not match number of message methods for button '{button_name}'")

        for key, methods in zip(mapping['keys'], keys_messages_methods):
            key_code = get_key_code(key)
            key_map[key_code] = methods

    return key_map


class FakeMidi:
    _instance = None

    @classmethod
    def get_fake_midi_if_exist(cls):
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, output_name='Fake MIDI Controller', key_map_file='config/fake_midi_key_map.json'):
        # Only initialize if it's the first time
        if not hasattr(self, '_initialized'):
            self.output_name = output_name
            self.output = mido.open_output(self.output_name, virtual=True)
            self.held_keys = set()
            self.relesed_keys = set()
            self.modifiers = {}
            self.key_map = load_key_map(key_map_file)
            self._initialized = True

    def handle_keys_input(self):
        amp = reduce(lambda s, m: s * (2 if m else 1),
                     self.modifiers.values(), 1)

        kwargs = {'step': amp, 'is_on': True, 'repeats': amp}
        pressed_keys_methods = [self.key_map[key][0]
                                for key in self.held_keys if key in self.key_map]
        relesed_keys_methods = [self.key_map[key][1]
                                for key in self.relesed_keys if key in self.key_map and self.key_map[key][1]]

        messages = []
        for methods in (pressed_keys_methods, relesed_keys_methods):
            for method in methods:
                message = method(**kwargs)
                messages += message
            kwargs['is_on'] = False # For released keys, set is_on to False

        for message in messages:
            self.output.send(message)

        for key in self.relesed_keys:
            self.held_keys.remove(key)
        self.relesed_keys.clear()

    def on_key_press(self, key, modifiers):
        if key in self.held_keys:
            return

        self.held_keys.add(key)
        self.modifiers = modifiers.__dict__

    def on_key_release(self, key):
        if key in self.held_keys:
            self.relesed_keys.add(key)

        self.modifiers = {}
