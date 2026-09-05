# SynMix

SynMix is a real-time visual synthesis application that renders animated fractal graphics using OpenGL shaders. It's designed as an interactive visual instrument where parameters can be controlled in real-time through MIDI or keyboard input.

## Technology Stack
- **Graphics**: ModernGL + ModernGL-Window for OpenGL rendering
- **Language**: Python 3.12
- **Dependency Management**: UV (modern Python package manager)
- **Shaders**: GLSL 3.3

## Installation

```bash
uv sync
```

## Run

**With real MIDI controller:**
```bash
uv run synmix
```

**With fake MIDI (keyboard control):**
```bash
uv run synmix --fakemidi
```

**Start with a specific scene:**
```bash
uv run synmix --start-scene "KeplerPlanet"
```

**With a specific MIDI controller config:**
```bash
uv run synmix --midi realop
```

**Full screen:**
```bash
uv run synmix --window glfw --fullscreen
```

**Alternative (run as Python module):**
```bash
python -m synmix
python -m synmix --fakemidi
```

**On WSL (Windows Subsystem for Linux):**
```bash
# Use uv.exe instead of uv for MIDI/audio driver access
uv.exe run synmix --fakemidi
```

## Configuration

### MIDI Controller

The MIDI mapping is data driven: each supported controller has a JSON file in
`src/synmix/resources/midi_config/`, selected with `--midi <name>` (defaults to `pioneer-ddj-t1`).

```json
{
  "name": "Mixage",
  "inc_scroll_value": 65,
  "dec_scroll_value": 63,
  "knobs": [
    { "label": "LEFT_HIGH", "event_type": "control_change", "value": 53 },
    { "label": "LEFT_MID", "event_type": "control_change", "value": 54, "channel": 2 }
  ],
  "scrollers": [
    { "label": "LEFT_WHEEL", "event_type": "control_change", "value": 36 }
  ],
  "clickables": [
    { "label": "RIGHT_LOAD", "event_type": "note_on", "value": 13 }
  ],
  "functions": {
    "next_scene": [["clickables", 0]],
    "decrease_speed": [["clickables", 15], ["clickables", 18]]
  }
}
```

- **`name`** is matched as a substring against the available MIDI input port names to find the device.
  It is independent of the file name: `--midi realop` loads `realop.json`, whose `name` is `Mixage`.
- **`knobs` / `scrollers` / `clickables`** list the controls of each `ButtonType`. `event_type` is one of
  `control_change`, `note_on` or `pitchwheel`, and `value` is the selector for that event: the control
  number, the note number, or the **channel** for `pitchwheel`.
- **`inc_scroll_value` / `dec_scroll_value`** are required: the values this device's scrollers send
  for one step up and one step down. They must differ and sit in `0`-`127`. `realop` sends `65`/`63`,
  the Pioneer DDJ-T1 sends `127`/`0`.
- **`channel`** is optional. Omitted, the button matches events on **any** channel; set to `0`-`15`,
  it matches only that channel, so two controls may share a control/note number on different channels.
  When both kinds are defined for the same number, the channel-specific one wins for its channel and
  the channel-less one catches the rest. `pitchwheel` entries must not set it - their `value` *is* the
  channel, which is how `LEFT_PITCH` and `RIGHT_PITCH` are told apart.
- **`label`** is optional and exists purely for readability - nothing looks a button up by it.
- **`functions`** binds application actions to buttons. Each action takes a list of `[section, index]`
  references, so an action can be reachable from more than one button. Supported actions:
  `next_scene`, `previous_scene`, `random_scene`, `time_offset`, `decrease_speed`, `increase_speed`.

Everything else - scene TOML files and the fake MIDI key map - addresses a button **positionally**, as
`[section, index]`. Adding support for a new controller therefore means dropping a new JSON into
`src/synmix/resources/midi_config/` that lists its controls in a comparable order; no scene file has to change.

### Fake MIDI Controller

The `--fakemidi` flag enables a virtual MIDI controller that maps keyboard inputs to MIDI messages

- Key mappings are configured in `src/synmix/resources/fake_midi_key_map.json`. This JSON file mirrors the section
  lists of the midi config, so entry `n` of `knobs` maps the keys for `["knobs", n]`:
  ```json
  { "knobs": [{ "label": "LEFT_HIGH", "keys": ["T", "Y"] }], "scrollers": [], "clickables": [] }
  ```
  - An entry may be `null` to leave that button unmapped, and `label` is optional readability only
  - Button behaviour (knob, scroller, clickable) comes from the section the button is listed in
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into the corresponding MIDI messages based on this configuration
- Modifiers (Shift, Ctrl, Alt) can be used in combination with mapped keys to accelerate changes for knobs and scrollers (not relevant for clickables)

#### Keyboard Mapping Table

| Button | Config Ref | Button Type | Key 1 | Key 2 |
|--------|------------|-------------|-------|-------|
| **LEFT_WHEEL** | `["scrollers", 0]` | Scroller | ↑ UP | ↓ DOWN |
| **RIGHT_WHEEL** | `["scrollers", 1]` | Scroller | ← LEFT | → RIGHT |
| **LEFT_PITCH** | `["knobs", 6]` | Knob | PAGE UP | PAGE DOWN |
| **RIGHT_PITCH** | `["knobs", 7]` | Knob | BACKSPACE | \ (Backslash) |
| **LEFT_LENGTH** | `["scrollers", 3]` | Scroller | Q | W |
| **LEFT_DRY_WET** | `["scrollers", 4]` | Scroller | A | S |
| **LEFT_GAIN** | `["knobs", 8]` | Knob | E | R |
| **LEFT_AMOUNT** | `["knobs", 9]` | Knob | D | F |
| **LEFT_HIGH** | `["knobs", 0]` | Knob | T | Y |
| **LEFT_MID** | `["knobs", 1]` | Knob | G | H |
| **LEFT_LOW** | `["knobs", 2]` | Knob | B | N |
| **RIGHT_HIGH** | `["knobs", 3]` | Knob | U | I |
| **RIGHT_MID** | `["knobs", 4]` | Knob | J | K |
| **RIGHT_LOW** | `["knobs", 5]` | Knob | M | , (Comma) |
| **RIGHT_LENGTH** | `["scrollers", 5]` | Scroller | O | P |
| **RIGHT_DRY_WET** | `["scrollers", 6]` | Scroller | L | ; (Semicolon) |
| **RIGHT_GAIN** | `["knobs", 10]` | Knob | [ | ] |
| **RIGHT_AMOUNT** | `["knobs", 11]` | Knob | . (Period) | / (Slash) |
| **LEFT_VOLUME** | `["knobs", 12]` | Knob | 9 | 0 |
| **RIGHT_VOLUME** | `["knobs", 13]` | Knob | - (Minus) | = (Equals) |
| **CROSSFADER** | `["knobs", 14]` | Knob | C | V |
| **CUEMIX** | `["knobs", 15]` | Knob | Z | X |
| **LEFT_CUE_1** | `["clickables", 3]` | Clickable | 1 | — |
| **LEFT_CUE_2** | `["clickables", 4]` | Clickable | 2 | — |
| **LEFT_CUE_3** | `["clickables", 5]` | Clickable | 3 | — |
| **LEFT_CUE_4** | `["clickables", 6]` | Clickable | 4 | — |
| **RIGHT_CUE_1** | `["clickables", 7]` | Clickable | 5 | — |
| **RIGHT_CUE_2** | `["clickables", 8]` | Clickable | 6 | — |
| **RIGHT_CUE_3** | `["clickables", 9]` | Clickable | 7 | — |
| **RIGHT_CUE_4** | `["clickables", 10]` | Clickable | 8 | — |
| **LEFT_SYNC** | `["clickables", 11]` | Clickable | F6 | — |
| **LEFT_RECORD** | `["clickables", 12]` | Clickable | F7 | — |
| **RIGHT_SYNC** | `["clickables", 13]` | Clickable | F8 | — |
| **RIGHT_RECORD** | `["clickables", 14]` | Clickable | F9 | — |
| **LEFT_MINUS** | `["clickables", 15]` | Clickable | F10 | — |
| **LEFT_PLUS** | `["clickables", 16]` | Clickable | F11 | — |
| **LEFT_SHIFT** | `["clickables", 17]` | Clickable | F12 | — |
| **RIGHT_MINUS** | `["clickables", 18]` | Clickable | HOME | — |
| **RIGHT_PLUS** | `["clickables", 19]` | Clickable | END | — |
| **RIGHT_SHIFT** | `["clickables", 20]` | Clickable | INSERT | — |
| **LEFT_IN** | `["clickables", 21]` | Clickable | DELETE | — |
| **LEFT_OUT** | `["clickables", 22]` | Clickable | ~ (Tilde) | — |
| **LEFT_FX_SEL** | `["clickables", 23]` | Clickable | ! (Exclamation) | — |
| **LEFT_FX_ON** | `["clickables", 24]` | Clickable | @ (At) | — |
| **RIGHT_IN** | `["clickables", 25]` | Clickable | # (Pound) | — |
| **RIGHT_OUT** | `["clickables", 26]` | Clickable | $ (Dollar) | — |
| **RIGHT_FX_SEL** | `["clickables", 27]` | Clickable | % (Percent) | — |
| **RIGHT_FX_ON** | `["clickables", 28]` | Clickable | ^ (Caret) | — |
| **RIGHT_LOAD** | `["clickables", 0]` | Clickable | F1 | — |
| **LEFT_LOAD** | `["clickables", 1]` | Clickable | F2 | — |
| **SCROLL** | `["scrollers", 2]` | Scroller | F3 | F4 |
| **SCROLL_CLICK** | `["clickables", 2]` | Clickable | F5 | — |

**Button Types:**
- **Knob**: Press first key to increase, second key to decrease (hold with Shift/Ctrl/Alt to apply modifiers)
- **Scroller**: Press first key to scroll up/right, second key to scroll down/left (modifiers adjust repeat rate)
- **Clickable**: Press the key to toggle on/off (no modifier support)

A standalone script is available at `scripts/fake_midi_monitor.py` for testing the fake MIDI controller and viewing MIDI output in real-time.
Run the script with:
```bash
uv run python scripts/fake_midi_monitor.py
```

### Scene Order

Scene order and navigation is controlled by `src/synmix/resources/scenes_order.toml`. This file determines:
- The order in which scenes are loaded
- Which scene starts first (index 0)
- The sequence when navigating between scenes

The first scene in the list will be loaded at startup by default. You can override this by using the `--start-scene` command-line argument to specify a different starting scene.

## Value Controllers

Parameters use value controllers defined in `src/synmix/params/valuecontrollers.py`. Each controller declares the `ButtonType`(s) it supports to prevent incompatible bindings when loading scenes:

- **NormalizedController** (`ButtonType.KNOB`) - Maps MIDI values to numeric ranges
- **RangedController** (`ButtonType.SCROLLER`) - Steps a value within fixed min/max bounds
- **CyclicController** (`ButtonType.SCROLLER`) - Like RangedController but wraps around
- **ToggleController** (`ButtonType.CLICKABLE`) - Flips boolean state on press
- **IsPressedController** (`ButtonType.CLICKABLE`) - Tracks button press state

Add custom controllers by decorating with `@register_controller("Name", supported_button_types...)`. Scene TOML files reference controllers by registered name.

## Project Structure

```
├── src/synmix/                    # Main package
│   ├── __main__.py                # Application entry point
│   ├── resource_loader.py         # Resource path resolution
│   ├── fakemidi/                  # Virtual MIDI utilities
│   │   └── fakemidi.py            # Fake MIDI controller implementation
│   ├── inputs/                    # Input handling system
│   │   ├── buttons.py             # Button / ButtonType definitions
│   │   ├── input_manager.py       # Input event processing
│   │   ├── midi_config.py         # Loads a controller mapping from resources/midi_config
│   │   └── midi.py                # MIDI event definitions
│   ├── params/                    # Parameter control system
│   │   ├── params.py              # Parameter definitions
│   │   └── valuecontrollers.py    # Parameter value controllers
│   ├── resources/                 # Data-driven content
│   │   ├── fake_midi_key_map.json # Keyboard to MIDI mapping
│   │   ├── scenes_order.toml      # Scene loading order
│   │   ├── midi_config/           # Per-controller MIDI mappings
│   │   │   ├── pioneer-ddj-t1.json
│   │   │   └── realop.json
│   │   ├── scenes/                # Scene parameter files (TOML)
│   │   ├── shaders/               # GLSL shader files
│   │   └── textures/              # Texture assets
│   ├── scenes/                    # Scene runtime logic
│   │   ├── scene.py
│   │   └── scenes_manager.py
│   └── top_level/                 # Entry-point helpers
│       ├── global_context.py
│       └── screen.py
├── scripts/
│   └── fake_midi_monitor.py       # Fake MIDI controller tester
└── tests/                         # pytest suite
    └── test_shaders.py            # Compiles every shader
```
