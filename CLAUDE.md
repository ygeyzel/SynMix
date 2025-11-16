# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
uv sync                    # Install dependencies and sync environment
```

### Running the Application
```bash
uv run main.py                              # Run with real MIDI controller
uv run main.py --fakemidi                   # Run with keyboard input (fake MIDI)
uv run main.py --start-scene "KeplerPlanet" # Start with specific scene
```

### Testing
```bash
uv run fakemidi/test_fake_midi.py          # Test fake MIDI controller functionality
```

## Architecture Overview

### Core Components
- **SynMix**: Real-time visual synthesis application rendering animated fractal graphics using OpenGL shaders
- **Scene System**: Data-driven scenes with TOML parameter files and corresponding GLSL shaders
- **Parameter Control**: Value controllers that map MIDI input to shader uniforms with type safety
- **Input Management**: MIDI input handling with optional fake MIDI for keyboard control

### Key Architectural Patterns

**Scene Management (`scenes/scenes_manager.py:30-50`)**:
- Scenes loaded from TOML files in `resources/scenes/`
- Scene order controlled by `resources/scenes_order.json`
- Each scene has corresponding GLSL shader in `resources/shaders/`
- Post-processing pipeline with dedicated shader

**Parameter System (`params/`)**:
- `valuecontrollers.py` defines controller types with `@register_controller` decorator
- Controllers enforce compatibility with button types (KNOB, SCROLLER, CLICKABLE)
- Scene TOML files reference controllers by registered name
- Type safety prevents incompatible button/controller pairings

**Input Architecture (`inputs/`)**:
- `buttons.py`: Button definitions and types
- `midi.py`: MIDI event definitions
- `input_manager.py`: MIDI event processing
- `fakemidi/`: Virtual MIDI controller for keyboard input

### Scene Structure
Each scene consists of:
1. **TOML parameter file** (`resources/scenes/*.toml`) - defines parameters and their controllers
2. **GLSL shader file** (`resources/shaders/*.glsl`) - implements visual effects
3. **Entry in scenes_order.json** - controls loading sequence

### Value Controller Types
- **NormalizedController**: Maps MIDI values to numeric ranges (KNOB buttons)
- **RangedController**: Incremental stepping with bounds (SCROLLER buttons)  
- **CyclicController**: Wrapping range stepping (SCROLLER buttons)
- **ToggleController**: Boolean state toggle (CLICKABLE buttons)
- **IsPressedController**: Button press state (CLICKABLE buttons)

### Fake MIDI System
- Keyboard-to-MIDI mapping in `resources/fake_midi_key_map.json`
- Maps button names to keyboard keys with modifier support
- Creates virtual MIDI port for keyboard input translation
- Button types determine interaction behavior (knob/scroller/clickable)

## Key File Locations

- `main.py`: Application entry point with argument parsing
- `top_level/screen.py`: Main rendering loop and OpenGL context
- `scenes/scenes_manager.py`: Scene loading, switching, and management
- `params/valuecontrollers.py`: Parameter controller registry and implementations
- `inputs/input_manager.py`: MIDI input event handling
- `resources/scenes_order.json`: Scene loading sequence configuration
- `resources/fake_midi_key_map.json`: Keyboard-to-MIDI mapping for fake controller

## Development Notes

### Adding New Scenes
1. Create GLSL shader in `resources/shaders/`
2. Create TOML parameter file in `resources/scenes/`
3. Add scene name to `resources/scenes_order.json`
4. Parameters must reference registered controller names from `valuecontrollers.py`

### Adding New Controllers
1. Create controller class in `params/valuecontrollers.py`
2. Decorate with `@register_controller("Name", ButtonType.KNOB)` 
3. Implement required methods for parameter updates
4. Reference by registered name in scene TOML files

### Time Parameters
Global time controls available via `top_level/global_context.py`:
- Time offset, speed, and hold interval adjustable via dedicated buttons
- Post-processing effects controlled separately from scene-specific parameters