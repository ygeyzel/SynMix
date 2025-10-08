import mido
from inputs.midi import MidiEventType, MidiGetter, get_midi_event_descriptor
from params.params import Param


class MidiInputManager:
    def __init__(self, midi_input_subname: str):
        self.bindings: dict[MidiGetter, Param] = {}
        try:
            midi_input_name = next(
                name for name in mido.get_input_names() if midi_input_subname in name
            )
            self.midi_input = mido.open_input(
                midi_input_name, callback=self._handle_midi_input)
        except StopIteration:
            raise ValueError(
                f"No MIDI input found with subname: {midi_input_subname}")

    def bind_param(self, param: Param, getter: MidiGetter):
        self.bindings[getter] = param

    def _handle_midi_input(self, event_msg: mido.Message):
        try:
            event_type = MidiEventType(event_msg.type)
            descriptor = get_midi_event_descriptor(event_type)

            event_dict = event_msg.dict()
            selector_value = event_dict[descriptor.SELECTOR_FIELD]
            binded_param = self.bindings.get(
                MidiGetter(event_type, selector_value))

            if not binded_param:
                print(f"No binding found for event: {event_dict}")
                return

            value = event_dict[descriptor.VALUE_FIELD]
            binded_param.control_param(value)
        except KeyError:
            print(f"Invalid MIDI event: {event_msg}")
