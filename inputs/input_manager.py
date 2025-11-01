from typing import Callable, List

import mido

from inputs.midi import MidiEventType, MidiGetter, get_midi_event_descriptor, MIDI_BUTTEN_CLICK
from params.params import Param



class MidiInputManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, input_subname: str=''):
        if not hasattr(self, '_initialized'):
            self.scenes_change_funcs = None
            self.param_bindings: dict[MidiGetter, Param] = {}
            self.general_funcs_bindings: dict[MidiGetter, Callable[[], None]] = {}
            try:
                midi_input_name = next(
                    name for name in mido.get_input_names() if input_subname in name
                )
                self.midi_input = mido.open_input(
                    midi_input_name, callback=self._handle_midi_input)

            except StopIteration:
                raise ValueError(f"No MIDI input found with subname: {input_subname=} in {mido.get_input_names()}. You may want to use --fakemidi")

            self._initialized = True

    def bind_param(self, param: Param):
        self.param_bindings[param.button.value] = param

    def unbind_params(self):
        self.param_bindings = {}

    def bind_general_funcs(self, event_selector: MidiGetter, afunc: Callable[[], None]):
        self.general_funcs_bindings[event_selector.value] = afunc

    def _handle_midi_input(self, event_msg: mido.Message):
        try:
            event_type = MidiEventType(event_msg.type)
            descriptor = get_midi_event_descriptor(event_type)

            event_dict = event_msg.dict()
            selector_value = event_dict[descriptor.SELECTOR_FIELD]
            event_selector = MidiGetter(event_type, selector_value)

            binded_param = self.param_bindings.get(event_selector)
            binded_func = self.general_funcs_bindings.get(event_selector)

            if not binded_param and not binded_func:
                print(f"No binding found for event: {event_dict}")
                return

            value = event_dict[descriptor.VALUE_FIELD]
            if binded_param:
                binded_param.control_param(value)
            else:
                if value == MIDI_BUTTEN_CLICK:
                    binded_func()

        except KeyError:
            print(f"Invalid MIDI event: {event_msg}")
