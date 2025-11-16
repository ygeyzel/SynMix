# SynMix

SynMix is a real-time visual synthesis application that renders animated fractal graphics using OpenGL shaders. It's designed as an interactive visual instrument where parameters can be controlled in real-time through keyboard input, with plans for MIDI integration.

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
uv run main.py
```

**With fake MIDI (keyboard control):**
```bash
uv run main.py --fakemidi
```

**Start with a specific scene:**
```bash
uv run main.py --start-scene "KeplerPlanet"
```

## Configuration

### Fake MIDI Controller

The `--fakemidi` flag enables a virtual MIDI controller that maps keyboard inputs to MIDI messages

- Key mappings are configured in `resources/fake_midi_key_map.json`. This JSON file maps:
  - Button names (from `inputs/buttons.py`) directly to the keyboard keys that trigger them
  - Button behaviour (knob, scroller, clickable) is derived from the `ButtonType` assigned in `inputs/buttons.py`
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into the corresponding MIDI messages based on this configuration
- Modifiers (Shift, Ctrl, Alt) can be used in combination with mapped keys to accelerate changes for knobs and scrollers (not relevant for clickables)

#### Keyboard Mapping Table

| Button | Button Type | Key 1 | Key 2 |
|--------|-------------|-------|-------|
| **LEFT_WHEEL** | Scroller | ↑ UP | ↓ DOWN |
| **RIGHT_WHEEL** | Scroller | → RIGHT | ← LEFT |
| **LEFT_PITCH** | Knob | \` (Backtick) | TAB |
| **RIGHT_PITCH** | Knob | BACKSPACE | \ (Backslash) |
| **LEFT_LENGTH** | Scroller | Q | W |
| **LEFT_DRY_WET** | Scroller | A | S |
| **LEFT_GAIN** | Knob | E | R |
| **LEFT_AMOUNT** | Knob | D | F |
| **LEFT_HIGH** | Knob | T | Y |
| **LEFT_MID** | Knob | G | H |
| **LEFT_LOW** | Knob | V | B |
| **RIGHT_HIGH** | Knob | U | I |
| **RIGHT_MID** | Knob | J | K |
| **RIGHT_LOW** | Knob | N | M |
| **RIGHT_LENGTH** | Scroller | O | P |
| **RIGHT_DRY_WET** | Scroller | L | ; (Semicolon) |
| **RIGHT_GAIN** | Knob | [ | ] |
| **RIGHT_AMOUNT** | Knob | . | / |
| **LEFT_VOLUME** | Knob | 9 | 0 |
| **RIGHT_VOLUME** | Knob | - (Minus) | + (Plus) |
| **CUEMIX** | Knob | Z | X |
| **LEFT_CUE_1** | Clickable | 1 | — |
| **LEFT_CUE_2** | Clickable | 2 | — |
| **LEFT_CUE_3** | Clickable | 3 | — |
| **LEFT_CUE_4** | Clickable | 4 | — |
| **RIGHT_CUE_1** | Clickable | 5 | — |
| **RIGHT_CUE_2** | Clickable | 6 | — |
| **RIGHT_CUE_3** | Clickable | 7 | — |
| **RIGHT_CUE_4** | Clickable | 8 | — |
| **LEFT_SYNC** | Clickable | F6 | — |
| **LEFT_RECORD** | Clickable | F7 | — |
| **RIGHT_SYNC** | Clickable | F8 | — |
| **RIGHT_RECORD** | Clickable | F9 | — |
| **LEFT_MINUS** | Clickable | F10 | — |
| **LEFT_PLUS** | Clickable | F11 | — |
| **LEFT_SHIFT** | Clickable | F12 | — |
| **RIGHT_MINUS** | Clickable | HOME | — |
| **RIGHT_PLUS** | Clickable | END | — |
| **RIGHT_SHIFT** | Clickable | INSERT | — |
| **LEFT_IN** | Clickable | DELETE | — |
| **LEFT_OUT** | Clickable | ~ (Tilde) | — |
| **LEFT_FX_SEL** | Clickable | ! (Exclamation) | — |
| **LEFT_FX_ON** | Clickable | @ (At) | — |
| **RIGHT_IN** | Clickable | # (Pound) | — |
| **RIGHT_OUT** | Clickable | $ (Dollar) | — |
| **RIGHT_FX_SEL** | Clickable | % (Percent) | — |
| **RIGHT_FX_ON** | Clickable | ^ (Caret) | — |
| **LEFT_LOAD** | Clickable | F2 | — |
| **RIGHT_LOAD** | Clickable | F1 | — |
| **SCROLL** | Scroller | F3 | F4 |
| **SCROLL_CLICK** | Clickable | F5 | — |
| **CROSSFADER** | Knob | . (Period) | / (Slash) | — |

**Button Types:**
- **Knob**: Press first key to increase, second key to decrease (hold with Shift/Ctrl/Alt to apply modifiers)
- **Scroller**: Press first key to scroll up/right, second key to scroll down/left (modifiers adjust repeat rate)
- **Clickable**: Press the key to toggle on/off (no modifier support)

A standalone test script is available at `fakemidi/test_fake_midi.py` for testing the fake MIDI controller and viewing MIDI output in real-time.
Run the script with:
```
uv run fakemidi/test_fake_midi.py
```

### Scene Order

Scene order and navigation is controlled by `resources/scenes_order.json`. This file determines:
- The order in which scenes are loaded
- Which scene starts first (index 0)
- The sequence when navigating between scenes

Example configuration:
```json
{
  "scene_order": [
    "UFO Blanket",
    "MengerFall",
    "DesertDunes",
    "CBSGalaxy",
    "QuaternionFractal",
    "KeplerPlanet",
    "WingsFractal"
  ]
}
```

To change the scene order:
1. Edit `resources/scenes_order.json`
2. Reorder the scene names in your desired sequence
3. Restart the application

The first scene in the list will be loaded at startup by default. You can override this by using the `--start-scene` command-line argument to specify a different starting scene. When you add new scenes, make sure to add their names to this configuration file.

## Value Controllers

Parameters use value controllers defined in `params/valuecontrollers.py`. Each controller declares the `ButtonType`(s) it supports to prevent incompatible bindings when loading scenes:

- **NormalizedController** (`ButtonType.KNOB`)  
  Maps incoming MIDI values (or pitch) into a configured numeric range.
- **RangedController** (`ButtonType.SCROLLER`)  
  Steps a value up or down within fixed min/max bounds using incremental MIDI messages.
- **CyclicController** (`ButtonType.SCROLLER`)  
  Similar to `RangedController`, but wraps around when exceeding the configured range.
- **ToggleController** (`ButtonType.CLICKABLE`)  
  Flips a boolean state whenever it receives a MIDI “on” message.
- **IsPressedController** (`ButtonType.CLICKABLE`)  
  Exposes whether the associated button is currently pressed.

Add custom controllers by decorating subclasses with `@register_controller("Name", supported_button_types...)`. Scene TOML files reference controllers by this registered name, and unsupported button/controller pairings raise a clear error during load.

## Project Structure

```
├── main.py              # Main application entry point
├── fakemidi/            # Virtual MIDI utilities
│   ├── fakemidi.py      # Fake MIDI controller implementation
│   └── test_fake_midi.py# Standalone tester
├── inputs/              # Input handling system
│   ├── buttons.py       # Button mapping definitions
│   ├── inputmanager.py  # Input event processing
│   └── midi.py          # MIDI event definitions
├── params/              # Parameter control system
│   ├── params.py        # Parameter definitions
│   └── valuecontrollers.py # Parameter value controllers
├── resources/           # Data-driven content
│   ├── fake_midi_key_map.json # Keyboard to MIDI mapping
│   ├── scenes_order.json      # Scene loading order
│   ├── scenes/                # Scene parameter files (TOML)
│   │   ├── cbs_galaxy.toml
│   │   ├── desert_dunes.toml
│   │   ├── kepler_planet.toml
│   │   ├── menger_fall.toml
│   │   ├── post_processing_params.toml
│   │   ├── quaternion_fractal.toml
│   │   ├── UFO_Blanket.toml
│   │   └── wings_fractal.toml
│   └── shaders/               # GLSL shader files
│       ├── cbs_galaxy.glsl
│       ├── desert_dunes.glsl
│       ├── kepler.glsl
│       ├── menger_fall.glsl
│       ├── post_processing.glsl
│       ├── quaternion_fractal.glsl
│       ├── UFO_Blanket.glsl
│       ├── vertex.glsl
│       └── wings.glsl
├── scenes/              # Scene runtime logic
│   ├── scene.py
│   └── scenes_manager.py
└── top_level/           # Entry-point helpers
    ├── global_context.py
    └── screen.py
```

```
