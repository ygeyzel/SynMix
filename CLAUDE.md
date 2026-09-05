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
uv run synmix --midi realop                # Use a specific MIDI controller config
# Alternative:
python -m synmix                           # Run as Python module
python -m synmix --fakemidi
```

### Testing
```bash
uv run pytest                              # Run tests (shader compile checks need an OpenGL context)
uv run python scripts/fake_midi_monitor.py # Interactively test fake MIDI controller
```

## Architecture Overview

### Core Components
- **SynMix**: Real-time visual synthesis application rendering animated fractal graphics using OpenGL shaders
- **Scene System**: Data-driven scenes with TOML parameter files and corresponding GLSL shaders
- **Parameter Control**: Value controllers that map MIDI input to shader uniforms with type safety
- **Input Management**: MIDI input handling with optional fake MIDI for keyboard control
- **MIDI Config**: Per-device button mappings loaded from JSON, selected with `--midi`

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
- Scene TOML `button` fields are `[section, index]` pairs resolved against the loaded `MidiConfig`
- Type safety prevents incompatible button/controller pairings

**Input Architecture (`src/synmix/inputs/`)**:
- `buttons.py`: `Button` (a midi getter + type + index + optional label) and `ButtonType`
- `midi.py`: MIDI event definitions
- `midi_config.py`: Loads `src/synmix/resources/midi_config/<name>.json` into a `MidiConfig`
- `input_manager.py`: MIDI event processing
- `src/synmix/fakemidi/`: Virtual MIDI controller for keyboard input

**MIDI Configuration (`src/synmix/resources/midi_config/*.json`)**:
- One file per physical controller, chosen with `--midi` (default `pioneer-ddj-t1`)
- `name` is matched as a substring against MIDI input port names to find the device
- `inc_scroll_value` / `dec_scroll_value` are required: the values this device's scrollers send
  for a step up / down (realop `65`/`63`, Pioneer DDJ-T1 `127`/`0`). Consumed by
  `IncDecController`, `ScrollerInterface` and `GlobalCtx.adjust_time_offset`
- `knobs` / `scrollers` / `clickables` list controls with `event_type` + `value`
  (control number, note number, or channel for `pitchwheel`); `label` is readability only
- `channel` is optional: omitted matches any channel, `0`-`15` pins the button to one, and a
  channel-specific button wins over a channel-less one on the same number. Not allowed on
  `pitchwheel` entries, whose `value` is already the channel
- `functions` binds actions (`next_scene`, `previous_scene`, `random_scene`, `time_offset`,
  `decrease_speed`, `increase_speed`) to lists of `[section, index]` button references
- Buttons are addressed positionally everywhere else, so a new controller needs only a new JSON

### Scene Structure
Each scene consists of:
1. **TOML parameter file** (`src/synmix/resources/scenes/*.toml`) - defines parameters and their controllers.
   Each param binds to a button positionally, e.g. `button = ["knobs", 1]`
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
- Mirrors the midi config sections: entry `n` of `knobs` maps the keys for `["knobs", n]`
  (an entry may be `null` to leave a button unmapped)
- Creates virtual MIDI port for keyboard input translation
- Button types determine interaction behavior (knob/scroller/clickable)

## Key File Locations

- `src/synmix/__main__.py`: Application entry point
- `src/synmix/top_level/screen.py`: Main rendering loop, OpenGL context and argument parsing
- `src/synmix/scenes/scenes_manager.py`: Scene loading, switching, and management
- `src/synmix/params/valuecontrollers.py`: Parameter controller registry and implementations
- `src/synmix/inputs/input_manager.py`: MIDI input event handling
- `src/synmix/inputs/midi_config.py`: MIDI controller config loading
- `src/synmix/resources/midi_config/`: Per-controller MIDI mappings (default `pioneer-ddj-t1.json`)
- `src/synmix/resources/scenes_order.toml`: Scene loading sequence configuration
- `src/synmix/resources/fake_midi_key_map.json`: Keyboard-to-MIDI mapping for fake controller
- `src/synmix/resource_loader.py`: Resource path resolution for package resources

## Development Notes

### Adding New Scenes
1. Create GLSL shader in `src/synmix/resources/shaders/`
2. Create TOML parameter file in `src/synmix/resources/scenes/`
3. Add scene name to `src/synmix/resources/scenes_order.json`
4. Parameters must reference registered controller names from `valuecontrollers.py`
5. Each param's `button` is a `[section, index]` pair into the midi config
   (`src/synmix/resources/midi_config/realop.json` lists the labels for each index)

### Adding New MIDI Controllers
1. Create `src/synmix/resources/midi_config/<Name>.json` with the device's controls, ordered comparably
   to the existing configs so scene bindings keep their meaning
2. Set `name` to a substring of the device's MIDI input port name
3. Run with `--midi <Name>`

### Adding New Controllers
1. Create controller class in `src/synmix/params/valuecontrollers.py`
2. Decorate with `@register_controller("Name", ButtonType.KNOB)`
3. Implement required methods for parameter updates
4. Reference by registered name in scene TOML files

### Time Parameters
Global time controls available via `src/synmix/top_level/global_context.py`:
- Time offset, speed, and hold interval adjustable via dedicated buttons
- Post-processing effects controlled separately from scene-specific parameters