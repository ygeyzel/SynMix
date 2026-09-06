import json
from collections.abc import Iterator
from pathlib import Path

import mido

from synmix.inputs.buttons import BUTTON_TYPE_BY_SECTION, Button
from synmix.inputs.midi import (
    MAX_CHANNEL,
    MIN_CHANNEL,
    MidiEventType,
    MidiGetter,
    ScrollMode,
    ScrollStep,
    decode_scroll,
)
from synmix.resource_loader import get_midi_config_dir

MIDI_CONFIG_DIR = get_midi_config_dir()


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
        self.scroll_mode = self._read_scroll_mode(data)
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

    def _read_scroll_mode(self, data: dict) -> ScrollMode:
        """How this device's scrollers encode a step, defaulting to direction only."""
        mode = data.get("scroll_mode")
        if mode is None:
            return ScrollMode.DIR_ONLY

        try:
            return ScrollMode(mode)
        except ValueError as exc:
            supported = ", ".join(scroll_mode.value for scroll_mode in ScrollMode)
            raise ValueError(
                f"Unsupported scroll_mode '{mode}' in midi config "
                f"'{self.config_name}'. Supported modes: {supported}."
            ) from exc

    def scroll_step(self, value: int) -> ScrollStep:
        """Get the direction and step count a scroller value carries on this device."""
        return decode_scroll(value, self.scroll_mode)

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

        channel = MidiConfig._read_channel(section, index, event_type, data)

        return Button(
            midi_getter=MidiGetter(event_type, data["value"], channel),
            button_type=BUTTON_TYPE_BY_SECTION[section],
            index=index,
            label=data.get("label"),
        )

    @staticmethod
    def _read_channel(
        section: str, index: int, event_type: MidiEventType, data: dict
    ) -> int | None:
        """
        An omitted channel matches events on any channel.

        pitchwheel events carry no selector other than their channel, so for them
        'value' is the channel and an explicit 'channel' would be ambiguous.
        """
        channel = data.get("channel")
        if channel is None:
            return None

        if event_type is MidiEventType.PITCH:
            raise ValueError(
                f"{section}[{index}] must not set 'channel' for "
                f"'{MidiEventType.PITCH.value}' events, where 'value' is the channel."
            )

        if not MIN_CHANNEL <= channel <= MAX_CHANNEL:
            raise ValueError(
                f"Channel {channel} of {section}[{index}] is out of range "
                f"({MIN_CHANNEL}-{MAX_CHANNEL})."
            )

        return channel

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
    def load(cls, config_name: str) -> "MidiConfig":
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

    @classmethod
    def iter_configs(cls) -> Iterator["MidiConfig"]:
        """Yield every config in MIDI_CONFIG_DIR, skipping any that fails to load."""
        for config_path in sorted(MIDI_CONFIG_DIR.glob("*.json")):
            try:
                yield cls.load(config_path.stem)
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                print(f"Warning: skipping midi config {config_path.name}: {exc}")

    @classmethod
    def detect_connected(cls) -> "MidiConfig":
        """Get the config of the first connected device, matched on its 'name'."""
        input_names = mido.get_input_names()
        for config in cls.iter_configs():
            if any(config.name in input_name for input_name in input_names):
                print(f"Detected midi device '{config.name}' ({config.config_name})")
                return config

        available = ", ".join(
            sorted(path.stem for path in MIDI_CONFIG_DIR.glob("*.json"))
        )
        raise ValueError(
            "No connected midi device matches any config. "
            f"Configs: {available}. Midi inputs: {input_names or 'none'}. "
            "You may want to use --midi or --fakemidi."
        )
