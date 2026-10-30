import argparse
import json
import sys
from pathlib import Path

import mido

# note_off is the release of a note_on, so both identify the same control
EVENT_TYPE_ALIASES = {"note_off": "note_on"}
VALUE_ATTRS = {"control_change": "control", "note_on": "note", "pitchwheel": "channel"}
SECTION_NAMES = ("knobs", "scrollers", "clickables")


def filtered_messages(mixer_name, channels=None, excluded=None):
    with mido.open_input(mixer_name) as mixer:
        for msg in mixer:
            channel = getattr(msg, "channel", None)
            if channels is not None and channel not in channels:
                continue
            if excluded and channel in excluded:
                continue
            yield msg


def control_entry(msg):
    """The config entry identifying the control that sent msg, or None if unsupported"""
    event_type = EVENT_TYPE_ALIASES.get(msg.type, msg.type)
    if event_type not in VALUE_ATTRS:
        return None
    entry = {"event_type": event_type, "value": getattr(msg, VALUE_ATTRS[event_type])}
    if event_type != "pitchwheel":  # a pitchwheel's value is already its channel
        entry["channel"] = msg.channel
    return entry


def same_control(known, entry):
    """Whether a known config entry identifies entry's control; no channel matches any"""
    return (
        known["event_type"] == entry["event_type"]
        and known["value"] == entry["value"]
        and known.get("channel", entry.get("channel")) == entry.get("channel")
    )


def matching_buttons(config, entry):
    """(section, index, button) for every button of config identifying entry's control"""
    return [
        (section, index, button)
        for section in SECTION_NAMES
        for index, button in enumerate(config.get(section, []))
        if same_control(button, entry)
    ]


def is_noise(msg, noise):
    entry = control_entry(msg)
    return entry is not None and any(same_control(known, entry) for known in noise)


class ConfigFile:
    """A midi_config JSON (as written by gen_config.py), reloaded whenever the file changes"""

    def __init__(self, path):
        self.path = Path(path)
        self.mtime = None
        self.data = {}

    @property
    def noise(self):
        return self.data.get("noise", [])

    def refresh(self):
        """Reload the file if it changed since the last read; True when it was (re)loaded"""
        try:
            mtime = self.path.stat().st_mtime_ns
        except FileNotFoundError:
            return False
        if mtime == self.mtime:
            return False
        try:
            with open(self.path) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            # likely caught mid-write; the old data stays and the next call retries
            print(f"Could not read {self.path} ({exc}), keeping its previous content")
            return False
        self.mtime, self.data = mtime, data
        return True


def find_port(device_name):
    """The input port whose name contains device_name, or None"""
    return next((name for name in mido.get_input_names() if device_name in name), None)


def main(mixer_name, channels=None, excluded=None, noise_file=None):
    for msg in filtered_messages(mixer_name, channels, excluded):
        if noise_file:
            if noise_file.refresh():
                print(f"Reloaded, silencing {len(noise_file.noise)} noise control(s)")
            if is_noise(msg, noise_file.noise):
                continue
        print(msg)


def mixers_selector():
    mixers = mido.get_input_names()
    if not mixers:
        print("No MIDI input devices found.")
        sys.exit(1)

    print("Available MIDI input devices:")
    for i, mixer in enumerate(mixers):
        print(f"{i + 1}: {mixer}")
    
    while True:
        try:
            choice = int(input("Select a mixer by number: ")) - 1
            if 0 <= choice < len(mixers):
                return mixers[choice]
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def channel_number(value):
    channel = int(value)
    if not 0 <= channel <= 15:
        raise argparse.ArgumentTypeError(f"channel must be between 0 and 15, got {value}")
    return channel


def build_parser(description="Print MIDI messages from an input device."):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("mixer_name", nargs="?", help="MIDI input device name (prompts if omitted)")
    parser.add_argument(
        "-c",
        "--channel",
        dest="channels",
        type=channel_number,
        action="append",
        metavar="0-15",
        help="only print messages on this channel (repeatable)",
    )
    parser.add_argument(
        "-f",
        "--filter-out",
        dest="excluded",
        type=channel_number,
        action="append",
        metavar="0-15",
        help="do not print messages on this channel (repeatable)",
    )
    return parser


def resolve_args(args):
    """Turn parsed shared CLI args into (mixer_name, channels, excluded)"""
    mixer_name = args.mixer_name or mixers_selector()
    channels = set(args.channels) if args.channels else None
    excluded = set(args.excluded) if args.excluded else None
    return mixer_name, channels, excluded


if __name__ == "__main__":
    parser = build_parser()
    parser.add_argument(
        "-s",
        "--silence",
        metavar="JSON",
        help="do not print the controls this midi_config JSON records as noise, "
        "reloading them whenever the file changes",
    )
    args = parser.parse_args()
    noise_file = ConfigFile(args.silence) if args.silence else None
    if noise_file:
        noise_file.refresh()
        print(f"Silencing {len(noise_file.noise)} noise control(s) from {args.silence}")
    main(*resolve_args(args), noise_file=noise_file)
