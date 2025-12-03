# SynMix

SynMix is a real-time visual synthesis application that renders animated fractal graphics using OpenGL shaders. It's designed as an interactive visual instrument where parameters can be controlled in real-time through MIDI controllers or keyboard input.

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

### Fake MIDI Controller

The `--fakemidi` flag enables a virtual MIDI controller that maps keyboard inputs to MIDI messages

- Key mappings are configured in `src/synmix/resources/fake_midi_key_map.toml`
- Maps button names (from `src/synmix/inputs/buttons.py`) to keyboard keys
- Button behaviour (knob, scroller, clickable) is derived from the `ButtonType` assigned in `buttons.py`
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into MIDI messages
- Modifiers (Shift, Ctrl, Alt) can be used to accelerate changes for knobs and scrollers

#### Keyboard Mapping Table

| Button | Button Type | Key 1 | Key 2 |
|--------|-------------|-------|-------|
| **LEFT_WHEEL** | Scroller | ↑ UP | ↓ DOWN |
| **RIGHT_WHEEL** | Scroller | ← LEFT | → RIGHT |
| **LEFT_PITCH** | Knob | PAGE UP | PAGE DOWN |
| **RIGHT_PITCH** | Knob | BACKSPACE | \ (Backslash) |
| **LEFT_LENGTH** | Scroller | Q | W |
| **LEFT_DRY_WET** | Scroller | A | S |
| **LEFT_GAIN** | Knob | E | R |
| **LEFT_AMOUNT** | Knob | D | F |
| **LEFT_HIGH** | Knob | T | Y |
| **LEFT_MID** | Knob | G | H |
| **LEFT_LOW** | Knob | B | N |
| **RIGHT_HIGH** | Knob | U | I |
| **RIGHT_MID** | Knob | J | K |
| **RIGHT_LOW** | Knob | M | , (Comma) |
| **RIGHT_LENGTH** | Scroller | O | P |
| **RIGHT_DRY_WET** | Scroller | L | ; (Semicolon) |
| **RIGHT_GAIN** | Knob | [ | ] |
| **RIGHT_AMOUNT** | Knob | . (Period) | / (Slash) |
| **LEFT_VOLUME** | Knob | 9 | 0 |
| **RIGHT_VOLUME** | Knob | - (Minus) | = (Equals) |
| **CROSSFADER** | Knob | C | V |
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
| **RIGHT_LOAD** | Clickable | F1 | — |
| **LEFT_LOAD** | Clickable | F2 | — |
| **SCROLL** | Scroller | F3 | F4 |
| **SCROLL_CLICK** | Clickable | F5 | — |

**Button Types:**
- **Knob**: Press first key to increase, second key to decrease (hold with Shift/Ctrl/Alt to apply modifiers)
- **Scroller**: Press first key to scroll up/right, second key to scroll down/left (modifiers adjust repeat rate)
- **Clickable**: Press the key to toggle on/off (no modifier support)

A standalone test script is available at `tests/test_fake_midi.py` for testing the fake MIDI controller and viewing MIDI output in real-time.
Run the script with:
```bash
python tests/test_fake_midi.py
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
│   │   ├── buttons.py             # Button mapping definitions
│   │   ├── input_manager.py       # Input event processing
│   │   └── midi.py                # MIDI event definitions
│   ├── params/                    # Parameter control system
│   │   ├── params.py              # Parameter definitions
│   │   └── valuecontrollers.py    # Parameter value controllers
│   ├── resources/                 # Data-driven content
│   │   ├── fake_midi_key_map.toml # Keyboard to MIDI mapping
│   │   ├── scenes_order.toml      # Scene loading order
│   │   ├── scenes/                # Scene parameter files (TOML)
│   │   ├── shaders/               # GLSL shader files
│   │   └── textures/              # Texture assets
│   ├── scenes/                    # Scene runtime logic
│   │   ├── scene.py
│   │   └── scenes_manager.py
│   └── top_level/                 # Entry-point helpers
│       ├── global_context.py
│       └── screen.py
└── tests/                         # Test scripts
    └── test_fake_midi.py          # Fake MIDI controller tester
```