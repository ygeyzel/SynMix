import json
from pathlib import Path

from synmix.inputs.buttons import BUTTON_TYPE_BY_SECTION, Button
from synmix.inputs.midi import MidiEventType, MidiGetter
from synmix.resource_loader import get_midi_config_dir

MIDI_CONFIG_DIR = get_midi_config_dir()
DEFAULT_MIDI_CONFIG = "Realop"


class MidiConfig:
    """
    Mapping of a physical MIDI device, loaded from resources/midi_config/<name>.json.

    Buttons are addressed positionally as (section, index), where section is one of
    'knobs', 'scrollers' or 'clickables'. The optional 'label' of each button is for
    readability only and is never used to look a button up.
    """

    def __init__(self, config_name: str, data: dict) -> None:
        self.config_name = config_name
        self.name = data["name"]
        self.buttons: dict[str, list[Button]] = {
            section: [
                self._generate_button(section, index, button_data)
                for index, button_data in enumerate(data.get(section, []))
            ]
            for section in BUTTON_TYPE_BY_SECTION
        }
        self.functions: dict[str, list[Button]] = {
            func_name: [self.get_button(*button_ref) for button_ref in button_refs]
            for func_name, button_refs in data.get("functions", {}).items()
        }

    def __repr__(self) -> str:
        sections = ", ".join(
            f"{section}={len(buttons)}" for section, buttons in self.buttons.items()
        )
        return f"MidiConfig({self.name}: {sections})"

    @staticmethod
    def _generate_button(section: str, index: int, data: dict) -> Button:
        try:
            event_type = MidiEventType(data["event_type"])
        except ValueError as exc:
            supported = ", ".join(event.value for event in MidiEventType)
            raise ValueError(
                f"Unsupported event_type '{data['event_type']}' for {section}[{index}]. "
                f"Supported event types: {supported}."
            ) from exc

        return Button(
            midi_getter=MidiGetter(event_type, data["value"]),
            button_type=BUTTON_TYPE_BY_SECTION[section],
            index=index,
            label=data.get("label"),
        )

    def get_button(self, section: str, index: int) -> Button:
        try:
            buttons = self.buttons[section]
        except KeyError as exc:
            supported = ", ".join(BUTTON_TYPE_BY_SECTION)
            raise ValueError(
                f"Unknown button section '{section}'. Supported sections: {supported}."
            ) from exc

        if not 0 <= index < len(buttons):
            raise ValueError(
                f"Button index {index} is out of range for '{section}' "
                f"in midi config '{self.config_name}' ({len(buttons)} buttons)."
            )

        return buttons[index]

    @classmethod
    def load(cls, config_name: str = DEFAULT_MIDI_CONFIG) -> "MidiConfig":
        config_path = MIDI_CONFIG_DIR / f"{Path(config_name).stem}.json"
        try:
            with config_path.open() as f:
                data = json.load(f)

        except FileNotFoundError as exc:
            available = ", ".join(
                sorted(path.stem for path in MIDI_CONFIG_DIR.glob("*.json"))
            )
            raise ValueError(
                f"No midi config found at {config_path}. "
                f"Available configs: {available}."
            ) from exc

        return cls(config_name, data)
