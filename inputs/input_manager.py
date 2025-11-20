import platform
from typing import Callable, Union

import mido

from inputs.buttons import Button
from inputs.midi import MidiEventType, MidiGetter, get_midi_event_descriptor
from params.params import Param


class MidiInputManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, input_subname: str = ""):
        if not hasattr(self, "_initialized"):
            self.scenes_change_funcs = None
            self.param_bindings: dict[MidiGetter, Param] = {}
            self.secondary_param_bindings: dict[MidiGetter, Param] = {}
            self.general_funcs_bindings: dict[MidiGetter, Callable[[int], None]] = {}
            self.fake_midi = None
            self.midi_input = None

            # Check if we're dealing with fake MIDI on Windows
            if (
                input_subname == "Fake MIDI Controller"
                and platform.system() == "Windows"
            ):
                # Import here to avoid circular import
                from top_level.global_context import GlobalCtx

                global_ctx = GlobalCtx()
                self.fake_midi = global_ctx.fake_midi
            else:
                try:
                    midi_input_name = next(
                        name for name in mido.get_input_names() if input_subname in name
                    )
                    self.midi_input = mido.open_input(
                        midi_input_name, callback=self._handle_midi_input
                    )

                except StopIteration:
                    raise ValueError(
                        f"No MIDI input found with subname: {input_subname=} in {mido.get_input_names()}. You may want to use --fakemidi"
                    )

            self._initialized = True

    def bind_param(self, param: Param):
        self.param_bindings[param.button.midi_getter] = param

    def bind_secondary_param(self, param: Param):
        self.secondary_param_bindings[param.button.midi_getter] = param

    def unbind_params(self):
        self.param_bindings = {}

    def bind_general_funcs(
        self, event_selector: Union[Button, MidiGetter], afunc: Callable[[int], None]
    ):
        midi_getter = (
            event_selector.midi_getter
            if isinstance(event_selector, Button)
            else event_selector
        )
        self.general_funcs_bindings[midi_getter] = afunc

    def _handle_midi_input(self, event_msg: mido.Message):
        try:
            event_type = MidiEventType(event_msg.type)
            descriptor = get_midi_event_descriptor(event_type)

            event_dict = event_msg.dict()
            selector_value = event_dict[descriptor.SELECTOR_FIELD]
            event_selector = MidiGetter(event_type, selector_value)

            binded_param = self.param_bindings.get(
                event_selector
            ) or self.secondary_param_bindings.get(event_selector)
            binded_func = self.general_funcs_bindings.get(event_selector)

            if not binded_param and not binded_func:
                print(f"No binding found for event: {event_dict}")
                return

            value = event_dict[descriptor.VALUE_FIELD]
            if binded_param:
                binded_param.control_param(value)
            else:
                binded_func(value)

        except KeyError:
            print(f"Invalid MIDI event: {event_msg}")

    def process_fake_midi_messages(self):
        """Process pending fake MIDI messages (Windows compatibility)"""
        if self.fake_midi:
            pending_messages = self.fake_midi.get_pending_messages()
            for message in pending_messages:
                self._handle_midi_input(message)
