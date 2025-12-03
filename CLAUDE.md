# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
```bash
uv sync                    # Install dependencies and sync environment
```

### WSL (Windows Subsystem for Linux) Notes
**Important**: On WSL, MIDI/audio drivers are not available in the Linux environment. To work around this, use the Windows executable `uv.exe` instead of `uv` to install dependencies and run the application. This ensures the code runs in a Windows context with access to the necessary drivers.

```bash
# On WSL, use uv.exe instead of uv:
uv.exe sync                           # Install dependencies
uv.exe run synmix --fakemidi          # Run application
uv.exe add <package>                  # Add new dependency
```

### Running the Application
```bash
uv run synmix                              # Run with real MIDI controller
uv run synmix --fakemidi                   # Run with keyboard input (fake MIDI)
uv run synmix --start-scene "KeplerPlanet" # Start with specific scene
# Alternative:
python -m synmix                           # Run as Python module
python -m synmix --fakemidi
```

### Testing
```bash
python tests/test_fake_midi.py             # Test fake MIDI controller functionality
```

## Architecture Overview

### Core Components
- **SynMix**: Real-time visual synthesis application rendering animated fractal graphics using OpenGL shaders
- **Scene System**: Data-driven scenes with TOML parameter files and corresponding GLSL shaders
- **Parameter Control**: Value controllers that map MIDI input to shader uniforms with type safety
- **Input Management**: MIDI input handling with optional fake MIDI for keyboard control

### Key Architectural Patterns

**Scene Management (`src/synmix/scenes/scenes_manager.py:30-50`)**:
- Scenes loaded from TOML files in `src/synmix/resources/scenes/`
- Scene order controlled by `src/synmix/resources/scenes_order.json`
- Each scene has corresponding GLSL shader in `src/synmix/resources/shaders/`
- Post-processing pipeline with dedicated shader

**Parameter System (`src/synmix/params/`)**:
- `valuecontrollers.py` defines controller types with `@register_controller` decorator
- Controllers enforce compatibility with button types (KNOB, SCROLLER, CLICKABLE)
- Scene TOML files reference controllers by registered name
- Type safety prevents incompatible button/controller pairings

**Input Architecture (`src/synmix/inputs/`)**:
- `buttons.py`: Button definitions and types
- `midi.py`: MIDI event definitions
- `input_manager.py`: MIDI event processing
- `src/synmix/fakemidi/`: Virtual MIDI controller for keyboard input

### Scene Structure
Each scene consists of:
1. **TOML parameter file** (`src/synmix/resources/scenes/*.toml`) - defines parameters and their controllers
2. **GLSL shader file** (`src/synmix/resources/shaders/*.glsl`) - implements visual effects
3. **Entry in scenes_order.json** - controls loading sequence

### Value Controller Types
- **NormalizedController**: Maps MIDI values to numeric ranges (KNOB buttons)
- **RangedController**: Incremental stepping with bounds (SCROLLER buttons)  
- **CyclicController**: Wrapping range stepping (SCROLLER buttons)
- **ToggleController**: Boolean state toggle (CLICKABLE buttons)
- **IsPressedController**: Button press state (CLICKABLE buttons)

### Fake MIDI System
- Keyboard-to-MIDI mapping in `src/synmix/resources/fake_midi_key_map.json`
- Maps button names to keyboard keys with modifier support
- Creates virtual MIDI port for keyboard input translation
- Button types determine interaction behavior (knob/scroller/clickable)

## Key File Locations

- `src/synmix/__main__.py`: Application entry point with argument parsing
- `src/synmix/top_level/screen.py`: Main rendering loop and OpenGL context
- `src/synmix/scenes/scenes_manager.py`: Scene loading, switching, and management
- `src/synmix/params/valuecontrollers.py`: Parameter controller registry and implementations
- `src/synmix/inputs/input_manager.py`: MIDI input event handling
- `src/synmix/resources/scenes_order.json`: Scene loading sequence configuration
- `src/synmix/resources/fake_midi_key_map.json`: Keyboard-to-MIDI mapping for fake controller
- `src/synmix/resource_loader.py`: Resource path resolution for package resources

## Development Notes

### Adding New Scenes
1. Create GLSL shader in `src/synmix/resources/shaders/`
2. Create TOML parameter file in `src/synmix/resources/scenes/`
3. Add scene name to `src/synmix/resources/scenes_order.json`
4. Parameters must reference registered controller names from `valuecontrollers.py`

### Adding New Controllers
1. Create controller class in `src/synmix/params/valuecontrollers.py`
2. Decorate with `@register_controller("Name", ButtonType.KNOB)`
3. Implement required methods for parameter updates
4. Reference by registered name in scene TOML files

### Time Parameters
Global time controls available via `src/synmix/top_level/global_context.py`:
- Time offset, speed, and hold interval adjustable via dedicated buttons
- Post-processing effects controlled separately from scene-specific parameters