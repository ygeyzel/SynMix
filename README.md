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


## Configuration

### Fake MIDI Controller

The `--fakemidi` flag enables a virtual MIDI controller that maps keyboard inputs to MIDI messages

- Key mappings are configured in `config/fake_midi_key_map.json`. This JSON file maps:
  - Button names (from `inputs/buttons.py`) to interface types (`STEPPER`, `SCROLLER`, `TOGGLE`)
  - Each button to specific keyboard keys
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into the corresponding MIDI messages based on this configuration
- Modifiers (Shift, Ctrl, Alt) can be used in combination with mapped keys to accelerate changes (not relevant for `TOGGLE` interface)

#### Keyboard Mapping Table

| Button | Parameter Control | Increase/On | Decrease/Off |
|--------|------------------|-------------|--------------|
| **LEFT_WHEEL** | Scrolling | ↑ (UP) | ↓ (DOWN) |
| **RIGHT_WHEEL** | Scrolling | → (RIGHT) | ← (LEFT) |
| **LEFT_HIGH** | Stepping | Q | A |
| **LEFT_MID** | Stepping | W | S |
| **LEFT_LOW** | Stepping | E | D |
| **RIGHT_HIGH** | Stepping | I | K |
| **RIGHT_MID** | Stepping | O | L |
| **RIGHT_LOW** | Stepping | P | ; (semicolon) |

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
    "KeplerPlanet",
    "Deadmau5Fractal"
  ]
}
```

To change the scene order:
1. Edit `config/scenes_order.json`
2. Reorder the scene names in your desired sequence
3. Restart the application

The first scene in the list will be loaded at startup. When you add new scenes, make sure to add their names to this configuration file.

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
