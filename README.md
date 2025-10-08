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

### Fake MIDI Controller

The `--fakemidi` flag enables a virtual MIDI controller that maps keyboard inputs to MIDI messages. This is useful for:

Key mappings are configured in `config/fake_midi_key_map.json`. This JSON file maps:
- Button names (from `inputs/buttons.py`) to interface types (`STEPPER`, `SCROLLER`, `TOGGLE`)
- Each button to specific keyboard keys
- The fake MIDI controller creates a virtual MIDI port and translates keyboard events into the corresponding MIDI messages based on this configuration
- Modifiers (Shift, Ctrl, Alt) can be used in combination with mapped keys to accelerate changes (not relevant for `TOGGLE` interface)


## Project Structure

```
├── main.py              # Main application entry point
├── config/              # Configuration files
│   └── fake_midi_key_map.json # Keyboard to MIDI mapping
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
