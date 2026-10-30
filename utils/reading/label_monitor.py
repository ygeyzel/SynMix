"""Print every MIDI message from a device next to the label a midi_config JSON gives it.

The config is reloaded whenever the file changes, so it can be watched while
gen_config.py fills it in. Controls the config records as noise are hidden unless
--show-noise is given. A message no config entry identifies is shown with "-".
"""

from main import (
    ConfigFile,
    build_parser,
    control_entry,
    filtered_messages,
    find_port,
    matching_buttons,
    resolve_args,
    same_control,
)

LABEL_WIDTH = 32
UNKNOWN = "-"
NOISE_LABEL = "NOISE"


def describe_buttons(config, entry):
    """The labels of the buttons identifying entry's control, with their positions"""
    return ", ".join(
        f"{button.get('label', '')} {section}[{index}]".strip()
        for section, index, button in matching_buttons(config, entry)
    )


def monitor(messages, config_file, show_noise=False):
    for msg in messages:
        if config_file.refresh():
            print(f"Reloaded {config_file.path}")
        entry = control_entry(msg)
        if entry is None:
            label = UNKNOWN
        elif any(same_control(known, entry) for known in config_file.noise):
            if not show_noise:
                continue
            label = NOISE_LABEL
        else:
            label = describe_buttons(config_file.data, entry) or UNKNOWN
        print(f"{label:{LABEL_WIDTH}} {msg}")


if __name__ == "__main__":
    parser = build_parser(
        "Print MIDI messages with the labels a midi_config JSON gives them."
    )
    parser.add_argument(
        "-j",
        "--config",
        required=True,
        metavar="JSON",
        help="midi_config JSON to read the labels from, reloaded whenever it changes",
    )
    parser.add_argument(
        "-n",
        "--show-noise",
        action="store_true",
        help="also print the controls the config records as noise, labelled NOISE",
    )
    args = parser.parse_args()
    config_file = ConfigFile(args.config)
    if not config_file.refresh():
        parser.error(f"cannot read {args.config}")
    if not args.mixer_name and config_file.data.get("name"):
        args.mixer_name = find_port(config_file.data["name"])
        if args.mixer_name:
            print(f"Using {args.mixer_name}")
    mixer_name, channels, excluded = resolve_args(args)
    try:
        monitor(
            filtered_messages(mixer_name, channels, excluded),
            config_file,
            args.show_noise,
        )
    except KeyboardInterrupt:
        pass
