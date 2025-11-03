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

- Key mappings are configured in `config/fake_midi_key_map.json`. This JSON file maps:
  - Button names (from `inputs/buttons.py`) to interface types (`STEPPER`, `SCROLLER`, `TOGGLE`)
  - Each button to specific keyboard keys
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into the corresponding MIDI messages based on this configuration
- Modifiers (Shift, Ctrl, Alt) can be used in combination with mapped keys to accelerate changes (not relevant for `TOGGLE` interface)

#### Keyboard Mapping Table

| Button | Control Type | Key 1 | Key 2 |
|--------|-------------|-------|-------|
| **LEFT_WHEEL** | Scroller | ↑ UP | ↓ DOWN |
| **RIGHT_WHEEL** | Scroller | → RIGHT | ← LEFT |
| **LEFT_PITCH** | Stepper | \` (Backtick) | TAB |
| **RIGHT_PITCH** | Stepper | BACKSPACE | \ (Backslash) |
| **LEFT_LENGTH** | Scroller | Q | W |
| **LEFT_DRY_WET** | Scroller | A | S |
| **LEFT_GAIN** | Stepper | E | R |
| **LEFT_AMOUNT** | Stepper | D | F |
| **LEFT_HIGH** | Stepper | T | Y |
| **LEFT_MID** | Stepper | G | H |
| **LEFT_LOW** | Stepper | V | B |
| **RIGHT_HIGH** | Stepper | U | I |
| **RIGHT_MID** | Stepper | J | K |
| **RIGHT_LOW** | Stepper | N | M |
| **RIGHT_LENGTH** | Scroller | O | P |
| **RIGHT_DRY_WET** | Scroller | L | ; (Semicolon) |
| **RIGHT_GAIN** | Stepper | [ | ] |
| **RIGHT_AMOUNT** | Stepper | . | / |
| **LEFT_VOLUME** | Stepper | 9 | 0 |
| **RIGHT_VOLUME** | Stepper | - (Minus) | + (Plus) |
| **CUEMIX** | Stepper | Z | X |
| **LEFT_CUE_1** | Toggle | 1 | — |
| **LEFT_CUE_2** | Toggle | 2 | — |
| **LEFT_CUE_3** | Toggle | 3 | — |
| **LEFT_CUE_4** | Toggle | 4 | — |
| **RIGHT_CUE_1** | Toggle | 5 | — |
| **RIGHT_CUE_2** | Toggle | 6 | — |
| **RIGHT_CUE_3** | Toggle | 7 | — |
| **RIGHT_CUE_4** | Toggle | 8 | — |
| **LEFT_SYNC** | Toggle | F6 | — |
| **LEFT_RECORD** | Toggle | F7 | — |
| **RIGHT_SYNC** | Toggle | F8 | — |
| **RIGHT_RECORD** | Toggle | F9 | — |
| **LEFT_LOAD** | Toggle | F2 | — |
| **RIGHT_LOAD** | Toggle | F1 | — |
| **SCROLL** | Scroller | F3 | F4 |
| **SCROLL_CLICK** | Toggle | F5 | — |

**Control Types:**
- **Stepper**: Press first key to increase, second key to decrease (hold with Shift/Ctrl/Alt for faster changes)
- **Scroller**: Press first key to scroll up/right, second key to scroll down/left (hold with Shift/Ctrl/Alt for faster scrolling)
- **Toggle**: Press the key to toggle on/off

A standalone test script is available at `scripts/test_fake_controller.py` for testing the fake MIDI controller and viewing MIDI output in real-time.
Run the script with:
```
uv run scripts/test_fake_controller.py
```

### Scene Order

Scene order and navigation is controlled by `config/scenes_order.json`. This file determines:
- The order in which scenes are loaded
- Which scene starts first (index 0)
- The sequence when navigating between scenes

Example configuration:
```json
{
  "scene_order": [
    "CBSGalaxy",
    "QuaternionFractal",
    "KeplerPlanet",
    "Deadmau5Fractal"
  ]
}
```

To change the scene order:
1. Edit `config/scenes_order.json`
2. Reorder the scene names in your desired sequence
3. Restart the application

The first scene in the list will be loaded at startup by default. You can override this by using the `--start-scene` command-line argument to specify a different starting scene. When you add new scenes, make sure to add their names to this configuration file.

## Project Structure

```
├── main.py              # Main application entry point
├── config/              # Configuration files
│   ├── fake_midi_key_map.json # Keyboard to MIDI mapping
│   └── scenes_order.json      # Scene loading order
├── inputs/              # Input handling system
│   ├── buttons.py       # Button mapping definitions
│   ├── inputmanager.py  # Input event processing
│   └── midi.py          # MIDI event definitions
├── params/              # Parameter control system
│   ├── params.py        # Parameter definitions
│   └── valuecontrollers.py # Parameter value controllers
├── scenes/              # Visual scenes
├── shaders/             # GLSL shader files
├── utils/               # Utility modules
│   └── fakemidi.py      # Virtual MIDI controller
└── resources/           # Additional resources
```

```
