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

**With real MIDI controller** (auto-detects which connected device matches a config):
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

**With a specific MIDI controller config** (skips auto-detection):
```bash
uv run synmix --midi pioneer-ddj-t1
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
`src/synmix/resources/midi_config/`.

Which config is used:

| Invocation | Config |
|---|---|
| `synmix` | auto-detected: the first config in `src/synmix/resources/midi_config/` whose `name` matches a connected MIDI input port. Errors listing the configs and the available ports if none match |
| `synmix --midi <name>` | that config, no detection |
| `synmix --fakemidi` | the fake controller's own mapping, generated in code - no physical device needed |
| `synmix --fakemidi --midi <name>` | that config, driven from the keyboard, to test a device you don't have on hand |

A config that fails to load is skipped during auto-detection with a warning, so one bad file does not
block startup; naming it explicitly with `--midi` still raises.

At startup the loaded config is reported against what the scenes actually bind:

```
Midi config 'pioneer-ddj-t1' has buttons no scene or function uses:
  knobs[16-26, 29-35]: FX1_DRY_WET, FX2_DRY_WET, FX1_CH1, FX1_CH2, (+14 more)
  clickables[11, 14, 17, 20-21, 27, 29-47, 49, 54-77]: L_KEY_LOCK, R_TEMPO_RAMGE, ... (+46 more)
```

Scenes bind buttons by label, so a control whose label no scene uses is silently dead. That is
expected for controls with no purpose yet, but a control you meant to use in the list usually means
its label in the config differs from the one in the scene file.

Some devices send the same midi data from two physical controls, and a config may list that data
under several labels. Bindings are keyed by the midi data, so if a scene binds two such labels to
different params (or a param and a post-processing param or function), only one of them responds.
Startup warns about each such pair:

```
Warning: in scene 'wings_fractal', buttons sharing midi data are bound to different targets, only one will respond:
  Button(LEFT_HIGH knobs[2]) -> 'hueShift' and Button(LEFT_HIGH_TWIN knobs[3]) -> 'brightness'
```

```json
{
  "name": "Mixage",
  "scroll_mode": "dir_only",
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
- **`scroll_mode`** is optional and says how this device's scrollers encode a step. The direction is
  fixed for every device - a value of `0`-`63` decreases, `64`-`127` increases - and the mode only
  decides whether the value carries a magnitude as well:
  - `dir_only` (the default) treats every event as a single step, whatever its value.
  - `accumulate` reads the magnitude from the distance to the outer end of the direction, so `127` is
    one step up, `126` two, `125` three, and `0` is one step down, `1` two, `2` three.
- **`channel`** is optional. Omitted, the button matches events on **any** channel; set to `0`-`15`,
  it matches only that channel, so two controls may share a control/note number on different channels.
  When both kinds are defined for the same number, the channel-specific one wins for its channel and
  the channel-less one catches the rest. `pitchwheel` entries must not set it - their `value` *is* the
  channel, which is how `LEFT_PITCH` and `RIGHT_PITCH` are told apart.
- **`label`** is how scenes find a button: a control is only usable from a scene if it has a label
  the scene files use. Several entries may share one label to drive the same params.
- **`functions`** binds application actions to buttons. Each action takes a list of `[section, index]`
  references, so an action can be reachable from more than one button. Supported actions:
  `next_scene`, `previous_scene`, `random_scene`, `time_offset`, `decrease_speed`, `increase_speed`.

Scene TOML files bind each param to a button by its **label**, e.g. `button = "A_MID"`. When several
buttons share a label - the same control mirrored on two channels - all of them drive the param. The
scenes use the labels of `pioneer-ddj-t1.json`, so a controller works with them when its config gives
its controls those labels; `realop.json` does not, and stops at startup with
`No button labelled 'L_WEEL' in midi config 'realop'`. The fake MIDI key map is still positional.

### Fake MIDI Controller

The `--fakemidi` flag enables a virtual MIDI controller that maps keyboard inputs to MIDI messages.
It is a device in its own right: with no `--midi` it generates its own mapping, sized to the key map,
so it works with no controller plugged in. Its knobs at indices 14 and 15 are `pitchwheel`, mirroring the
real devices, so params declaring `is_pitch` keep their full range, and it generates the same
`functions` bindings the real configs use:

| Key | Action |
|-----|--------|
| F1 / F2 | next / previous scene |
| F5 | random scene |
| F3 / F4 | time offset forward / back |
| F11 or END | increase speed (hold to repeat) |
| F10 or HOME | decrease speed (hold to repeat) |

- Key mappings are configured in `src/synmix/resources/fake_midi_key_map.json`. This JSON file mirrors the section
  lists of the midi config, so entry `n` of `knobs` maps the keys for `["knobs", n]`:
  ```json
  {
    "knobs":      [["T", "Y"], ["G", "H"]],
    "scrollers":  [["UP", "DOWN"]],
    "clickables": ["F1", "F2"]
  }
  ```
  - Knobs and scrollers take two keys (increase, decrease), clickables a single key
  - An entry may be `null` to leave that button unmapped
  - Button behaviour (knob, scroller, clickable) comes from the section the button is listed in
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into the corresponding MIDI messages based on this configuration
- Modifiers (Shift, Ctrl, Alt) can be used in combination with mapped keys to accelerate changes for knobs and scrollers (not relevant for clickables)

#### Keyboard Mapping Table

| Button | Config Ref | Button Type | Key 1 | Key 2 |
|--------|------------|-------------|-------|-------|
| **L_WEEL** | `["scrollers", 0]` | Scroller | ↑ UP | ↓ DOWN |
| **R_WEEL** | `["scrollers", 1]` | Scroller | ← LEFT | → RIGHT |
| **L_TEMPO** | `["knobs", 14]` | Knob | PAGE UP | PAGE DOWN |
| **R_TEMPO** | `["knobs", 15]` | Knob | BACKSPACE | \ (Backslash) |
| **L_MOVE_GRID** | `["scrollers", 3]` | Scroller | Q | W |
| **L_WEEL_SCRETCH** | `["scrollers", 4]` | Scroller | A | S |
| **A_GAIN** | `["knobs", 8]` | Knob | E | R |
| **L_FILTER** | `["knobs", 9]` | Knob | D | F |
| **A_HI** | `["knobs", 2]` | Knob | T | Y |
| **A_MID** | `["knobs", 3]` | Knob | G | H |
| **A_LOW** | `["knobs", 4]` | Knob | B | N |
| **B_HI** | `["knobs", 5]` | Knob | U | I |
| **B_MID** | `["knobs", 6]` | Knob | J | K |
| **B_LOW** | `["knobs", 7]` | Knob | M | , (Comma) |
| **R_MOVE_GRID** | `["scrollers", 5]` | Scroller | O | P |
| **R_WEEL_SCRETCH** | `["scrollers", 6]` | Scroller | L | ; (Semicolon) |
| **B_GAIN** | `["knobs", 10]` | Knob | [ | ] |
| **R_FILTER** | `["knobs", 11]` | Knob | . (Period) | / (Slash) |
| **C_GAIN** | `["knobs", 0]` | Knob | 9 | 0 |
| **D_GAIN** | `["knobs", 1]` | Knob | - (Minus) | = (Equals) |
| **FADER** | `["knobs", 12]` | Knob | C | V |
| **HEADPHONES_MIX** | `["knobs", 13]` | Knob | Z | X |
| **L_HOT_CUE** | `["clickables", 3]` | Clickable | 1 | — |
| **L_ACTIVE** | `["clickables", 4]` | Clickable | 2 | — |
| **L_DEL** | `["clickables", 5]` | Clickable | 3 | — |
| **L_MOVE_GRID_BTN** | `["clickables", 6]` | Clickable | 4 | — |
| **R_HOT_CUE** | `["clickables", 7]` | Clickable | 5 | — |
| **R_PLAY** | `["clickables", 8]` | Clickable | 6 | — |
| **R_CUE** | `["clickables", 9]` | Clickable | 7 | — |
| **R_MOVE_GRID_BTN** | `["clickables", 10]` | Clickable | 8 | — |
| **L_KEY_LOCK** | `["clickables", 11]` | Clickable | F6 | — |
| **L_TEMPO_RAMGE** | `["clickables", 12]` | Clickable | F7 | — |
| **R_KEY_LOCK** | `["clickables", 13]` | Clickable | F8 | — |
| **R_TEMPO_RAMGE** | `["clickables", 14]` | Clickable | F9 | — |
| **L_BWD** | `["clickables", 15]` | Clickable | F10 | — |
| **L_FWD** | `["clickables", 16]` | Clickable | F11 | — |
| **L_FUNC** | `["clickables", 17]` | Clickable | F12 | — |
| **R_BWD** | `["clickables", 18]` | Clickable | HOME | — |
| **R_FWD** | `["clickables", 19]` | Clickable | END | — |
| **R_FUNC** | `["clickables", 20]` | Clickable | INSERT | — |
| **L_IN_ADJUST** | `["clickables", 21]` | Clickable | DELETE | — |
| **L_OUT_ADJUST** | `["clickables", 22]` | Clickable | ~ (Tilde) | — |
| **FX1_ADVENCED** | `["clickables", 23]` | Clickable | ! (Exclamation) | — |
| **FX1_DRY_WET_BTN** | `["clickables", 24]` | Clickable | @ (At) | — |
| **R_IN_ADJUST** | `["clickables", 25]` | Clickable | # (Pound) | — |
| **R_OUT_ADJUST** | `["clickables", 26]` | Clickable | $ (Dollar) | — |
| **FX2_ADVENCED** | `["clickables", 27]` | Clickable | % (Percent) | — |
| **FX2_DRY_WET_BTN** | `["clickables", 28]` | Clickable | ^ (Caret) | — |
| **B_LOAD** | `["clickables", 0]` | Clickable | F1 | — |
| **A_LOAD** | `["clickables", 1]` | Clickable | F2 | — |
| **MID_WEEL** | `["scrollers", 2]` | Scroller | F3 | F4 |
| **MID_WEEL_BTN** | `["clickables", 2]` | Clickable | F5 | — |

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
