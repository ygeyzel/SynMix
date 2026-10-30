"""Build a midi_config dict (and JSON) by playing with the controls of a device.

Move one control (or several), press Enter, and the captured messages are analysed:
the control is identified, 14-bit MSB/LSB pairs are folded into the MSB, and a section
is suggested. Confirm or change it, give a label, and repeat. Type q to finish and
write the JSON.

With --resume <file.json> an existing config is loaded and the new controls are
appended to it, written back to the same file unless -o says otherwise. With
--regen <file.json> the config is started over and saved in place of that file.

A control answered as noise is saved in the config's "noise" list and from then on
silently dropped from every capture.
"""

import json
import os
import queue
import re
import threading
from itertools import pairwise
from pathlib import Path

try:
    import readline
except ImportError:  # e.g. Windows without pyreadline: no line editing or history
    readline = None
else:
    # Only the label prompt gets a history; the other answers are too short to recall
    readline.set_auto_history(False)

from main import (
    SECTION_NAMES,
    build_parser,
    control_entry,
    filtered_messages,
    find_port,
    matching_buttons,
    resolve_args,
    same_control,
)

SECTIONS = dict(zip("ksc", SECTION_NAMES))
SKIP = "x"
NOISE = "n"
# relative encoders only send values hugging the ends of the range
SCROLLER_MARGIN = 16
MIN_PAIR_MESSAGES = 4


def entry_key(entry):
    return tuple(entry.values())


def capture_messages(messages):
    """Start collecting messages in the background; returns the queue they land in"""
    captured = queue.Queue()

    def pump():
        for msg in messages:
            captured.put(msg)

    threading.Thread(target=pump, daemon=True).start()
    return captured


def drain(captured):
    msgs = []
    while not captured.empty():
        msgs.append(captured.get_nowait())
    return msgs


def group_controls(msgs):
    """{key: (entry, [cc values])} in order of first appearance, plus the key sequence"""
    groups, sequence = {}, []
    for msg in msgs:
        entry = control_entry(msg)
        if entry is None:
            continue
        key = entry_key(entry)
        groups.setdefault(key, (entry, []))
        if msg.type == "control_change":
            groups[key][1].append(msg.value)
        sequence.append(key)
    return groups, sequence


def value_changes(values):
    return sum(a != b for a, b in pairwise(values))


def drop_lsb_controls(groups, sequence):
    """Remove the LSB of each 14-bit pair: two CCs on a channel that strictly alternate.

    The MSB is the one whose value changes less often. Pairing is read from the data
    rather than assumed from the control numbers.
    """
    ccs = [
        key
        for key, (entry, _) in groups.items()
        if entry["event_type"] == "control_change"
    ]
    dropped = set()
    for i, a in enumerate(ccs):
        for b in ccs[i + 1 :]:
            same_channel = groups[a][0]["channel"] == groups[b][0]["channel"]
            both = [key for key in sequence if key in (a, b)]
            alternate = all(x != y for x, y in pairwise(both))
            if same_channel and alternate and len(both) >= MIN_PAIR_MESSAGES * 2:
                lsb = max((a, b), key=lambda key: value_changes(groups[key][1]))
                dropped.add(lsb)
    return {key: group for key, group in groups.items() if key not in dropped}, dropped


def suggest_section(entry, values):
    if entry["event_type"] == "note_on":
        return "clickables"
    if (
        entry["event_type"] == "control_change"
        and values
        and all(v < SCROLLER_MARGIN or v > 127 - SCROLLER_MARGIN for v in values)
    ):
        return "scrollers"
    return "knobs"


def describe(entry, values):
    span = f", values {min(values)}..{max(values)}" if values else ""
    return f"{entry}{span}"


def ask_section(suggested):
    """A section name, NOISE, or None to skip"""
    default = next(letter for letter, name in SECTIONS.items() if name == suggested)
    options = "/".join(f"[{letter}]{name}" for letter, name in SECTIONS.items())
    while True:
        choice = (
            input(
                f"  {options} / [{NOISE}] noise / [{SKIP}] skip (Enter = {default}): "
            )
            .strip()
            .lower()
            or default
        )
        if choice == SKIP:
            return None
        if choice == NOISE:
            return NOISE
        if choice in SECTIONS:
            return SECTIONS[choice]
        print("  Please answer k, s, c, n or x.")


def record_noise(config, entry):
    config.setdefault("noise", []).append(entry)
    print("  Recorded as noise, it will be ignored from now on.")


def input_with_history(prompt, history):
    """input() where the up arrow walks back through history, newest first, for editing"""
    if readline is None:
        return input(prompt)
    readline.clear_history()
    for item in history:
        readline.add_history(item)
    try:
        return input(prompt)
    finally:
        readline.clear_history()


def label_history(config):
    """The labels already in config, oldest first, to seed the label prompt's history"""
    return [
        button["label"]
        for section in SECTIONS.values()
        for button in config[section]
        if button.get("label")
    ]


def add_control(config, entry, values, history):
    section = ask_section(suggest_section(entry, values))
    if section is None:
        return
    if section == NOISE:
        record_noise(config, entry)
        return
    label = input_with_history("  label: ", history).strip().upper().replace(" ", "_")
    label = label or f"{section.upper()}_{len(config[section])}"
    config[section].append({"label": label, **entry})
    if not history or history[-1] != label:
        history.append(label)


def known_labels(config, entry):
    """Labels config already has for the control"""
    return [
        button.get("label") or f"{section}[{index}]"
        for section, index, button in matching_buttons(config, entry)
    ]


def drop_noise(groups, sequence, config):
    """Remove the controls recorded as noise, before anything else looks at them"""
    noise = config.get("noise", [])
    kept = {
        key: group
        for key, group in groups.items()
        if not any(same_control(known, group[0]) for known in noise)
    }
    return kept, [key for key in sequence if key in kept]


def ask_another_label(labels):
    """
    'y' to label the data again, as some devices send it from two controls,
    'm' to mark it as noise, anything else to leave it
    """
    answer = input(
        f"  Already have it as {', '.join(labels)}. "
        "Add another label? [y]es / [m]ark as noise / [N]o: "
    )
    return answer.strip().lower()


def load_config(path):
    """Load a config, making sure every section exists"""
    with open(path) as f:
        config = json.load(f)
    for section in SECTIONS.values():
        config.setdefault(section, [])
    return config


def summary(config):
    counts = [f"{len(config[section])} {section}" for section in SECTIONS.values()]
    if config.get("noise"):
        counts.append(f"{len(config['noise'])} noise")
    return ", ".join(counts)


def to_json(config):
    """Indented JSON, keeping lists of plain values such as ["clickables", 0] on one line"""
    text = json.dumps(config, indent=2)
    return re.sub(
        r"\[\s*([^\[\]{}]*?)\s*\]",
        lambda m: "[" + re.sub(r",\s+", ", ", m.group(1)) + "]",
        text,
    )


def write_json(path, config):
    """Write config to path atomically, so a reader such as main.py -s never sees half a file"""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(to_json(config) + "\n")
    os.replace(tmp, path)


def collect_config(captured, config, on_change=None):
    """Repeatedly capture a played control, analyse it and add it to config.

    on_change is called after every answer that changed config.
    """
    history = label_history(config)
    drain(captured)
    while True:
        answer = (
            input("Move a control, then press Enter (q + Enter to finish): ")
            .strip()
            .lower()
        )
        if answer == "q":
            return
        groups, sequence = drop_noise(*group_controls(drain(captured)), config)
        groups, dropped = drop_lsb_controls(groups, sequence)
        for key, (entry, values) in groups.items():
            before = to_json(config)
            print(describe(entry, values))
            labels = known_labels(config, entry)
            answer = ask_another_label(labels) if labels else "y"
            if answer == "m":
                record_noise(config, entry)
            elif answer == "y":
                add_control(config, entry, values, history)
            if on_change and to_json(config) != before:
                on_change()
        for key in dropped:
            print(f"Ignored {key}: LSB of a 14-bit control")
        if not groups:
            print("Nothing captured.")


if __name__ == "__main__":
    parser = build_parser(
        "Generate a midi_config dict by playing with the controls of a device."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="JSON file, or a directory to put <device_name>.json in "
        "(default: the --resume file, else stdout)",
    )
    existing = parser.add_mutually_exclusive_group()
    existing.add_argument(
        "-r",
        "--resume",
        metavar="JSON",
        help="existing config to load and append the new controls to",
    )
    existing.add_argument(
        "-g",
        "--regen",
        metavar="JSON",
        help="config to start over from scratch and save in its place, "
        "keeping its recorded noise",
    )
    args = parser.parse_args()
    old = None
    if args.resume:
        old = load_config(args.resume)
        print(f"Loaded {args.resume}: {summary(old)}")
    elif args.regen and Path(args.regen).exists():
        old = load_config(args.regen)
        print(f"Regenerating {args.regen}, replacing its {summary(old)}")
    if old and not args.mixer_name:
        args.mixer_name = find_port(old["name"])
        if args.mixer_name:
            print(f"Using {args.mixer_name}")
    mixer_name, channels, excluded = resolve_args(args)
    device_name = mixer_name.split(":")[0]  # drop the ALSA ":<port> <id>" suffix
    if args.resume:
        config = old
    else:
        config = {"name": device_name, **{section: [] for section in SECTIONS.values()}}
        if old and old.get("noise"):  # the device's bad signals don't change on a regen
            config["noise"] = old["noise"]
    existing_file = args.resume or args.regen
    output = args.output or existing_file
    if output:
        output = Path(output)
        if output.is_dir():
            output /= device_name.replace(" ", "_").lower() + ".json"
    loaded = to_json(config)

    def save():
        write_json(output, config)
        print(f"  Saved {output}")

    try:
        messages = filtered_messages(mixer_name, channels, excluded)
        collect_config(capture_messages(messages), config, save if output else None)
    except (KeyboardInterrupt, EOFError):
        pass
    unchanged = to_json(config) == loaded
    if existing_file and not args.output and unchanged and output.exists():
        print(f"Nothing added, {output} left unchanged.")
    elif output:
        write_json(output, config)
        print(f"Wrote {output}: {summary(config)}")
    else:
        print(to_json(config))
