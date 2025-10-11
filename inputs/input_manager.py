import mido

from inputs.midi import MidiEventType, MidiGetter, get_midi_event_descriptor
from params.params import Param



class MidiInputManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, input_subname: str=''):
        if not hasattr(self, '_initialized'):
            self.bindings: dict[MidiGetter, Param] = {}
            try:
                midi_input_name = next(
                    name for name in mido.get_input_names() if input_subname in name
                )
                self.midi_input = mido.open_input(
                    midi_input_name, callback=self._handle_midi_input)

            except StopIteration:
                raise ValueError(
                    f"No MIDI input found with subname: {midi_input_subname}")

            self._initialized = True

    def bind_param(self, param: Param):
        self.bindings[param.button.value] = param

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
