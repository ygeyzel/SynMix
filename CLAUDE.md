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
uv run synmix                              # Auto-detect the connected MIDI controller
uv run synmix --fakemidi                   # Run with keyboard input (fake MIDI)
uv run synmix --start-scene "KeplerPlanet" # Start with specific scene
uv run synmix --midi pioneer-ddj-t1        # Use a specific MIDI controller config
uv run synmix --fakemidi --midi pioneer-ddj-t1  # Drive a device's mapping from the keyboard
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
- Scene TOML `button` fields are midi config labels (e.g. `"A_MID"`), resolved with
  `MidiConfig.get_buttons_by_label`; a label shared by several buttons (one control on two
  channels) binds all of them to the param, so `Param.buttons` is a tuple
- Type safety prevents incompatible button/controller pairings

**Input Architecture (`src/synmix/inputs/`)**:
- `buttons.py`: `Button` (a midi getter + type + index + optional label) and `ButtonType`
- `midi.py`: MIDI event definitions
- `midi_config.py`: Loads `src/synmix/resources/midi_config/<name>.json` into a `MidiConfig`
- `input_manager.py`: MIDI event processing
- `src/synmix/fakemidi/`: Virtual MIDI controller for keyboard input

**MIDI Configuration (`src/synmix/resources/midi_config/*.json`)**:
- One file per physical controller. With no `--midi`, `MidiConfig.detect_connected()` picks the
  first config whose `name` matches a connected MIDI input port, skipping configs that fail to
  load; `--fakemidi` without `--midi` uses the fake controller's own generated mapping instead
- `name` is matched as a substring against MIDI input port names to find the device
- Scroller values are read by direction: `0`-`63` decrease, `64`-`127` increase
- `scroll_mode` is optional, `dir_only` (default) or `accumulate`. Under `dir_only` an event is
  one step whatever its value; under `accumulate` the value also carries the magnitude, growing
  with the distance from the outer end of its direction (`127` one step up, `126` two, `0` one
  step down, `1` two). Decoded by `decode_scroll` in `inputs/midi.py`, reached through
  `MidiConfig.scroll_step` from `IncDecController` and `GlobalCtx.adjust_time_offset`
- `knobs` / `scrollers` / `clickables` list controls with `event_type` + `value`
  (control number, note number, or channel for `pitchwheel`); `label` is what scenes bind to
- `channel` is optional: omitted matches any channel, `0`-`15` pins the button to one, and a
  channel-specific button wins over a channel-less one on the same number. Not allowed on
  `pitchwheel` entries, whose `value` is already the channel
- `functions` binds actions (`next_scene`, `previous_scene`, `random_scene`, `time_offset`,
  `decrease_speed`, `increase_speed`) to lists of `[section, index]` button references
- Scenes use the labels of `pioneer-ddj-t1.json`; a config without them (e.g. `realop.json`) fails
  at startup with "No button labelled ...". The fake MIDI key map stays positional
- `ScenesManager._report_unused_buttons` prints, at startup, the config's buttons that no scene
  param, post param or function binds. A control you meant to use there usually has a label
  that differs from the one in the scene file, and will silently do nothing
- `ScenesManager._report_shared_midi_bindings` warns when buttons sharing (overlapping) midi data
  are bound to different targets in a scene - bindings are keyed by midi data, so only one responds

### Scene Structure
Each scene consists of:
1. **TOML parameter file** (`src/synmix/resources/scenes/*.toml`) - defines parameters and their controllers.
   Each param binds to a button by its midi config label, e.g. `button = "A_MID"`
2. **GLSL shader file** (`src/synmix/resources/shaders/*.glsl`) - implements visual effects
3. **Entry in scenes_order.json** - controls loading sequence

### Value Controller Types
- **NormalizedController**: Maps MIDI values to numeric ranges (KNOB buttons). When a param
  declares `is_pitch`, ScenesManager sets it from the bound button (true only for `pitchwheel`),
  so a pitch slot also gets the right range on a device whose control there is a plain 0-127 CC
- **RangedController**: Incremental stepping with bounds (SCROLLER buttons)  
- **CyclicController**: Wrapping range stepping (SCROLLER buttons)
- **ToggleController**: Boolean state toggle (CLICKABLE buttons)
- **IsPressedController**: Button press state (CLICKABLE buttons)

### Fake MIDI System
- Keyboard-to-MIDI mapping in `src/synmix/resources/fake_midi_key_map.json`
- Mirrors the midi config sections: entry `n` of `knobs` maps the keys for `["knobs", n]`.
  Knobs/scrollers take two keys (`["T", "Y"]`), clickables one (`"F1"`), `null` leaves it unmapped
- Not tied to a device: `generate_midi_config` builds its own mapping sized to the key map,
  with `pitchwheel` at knob indices 14 and 15 so `is_pitch` params keep their range
- It also generates `functions` from `FAKE_MIDI_FUNCTIONS`, at the same positions the real
  configs use, so F1/F2/F5 switch scenes, F3/F4 shift time and F10/F11 or HOME/END change speed
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
5. Each param's `button` is a label from the midi config
   (`src/synmix/resources/midi_config/pioneer-ddj-t1.json` lists them); pytest checks they exist

### Adding New MIDI Controllers
1. Create `src/synmix/resources/midi_config/<Name>.json` (e.g. with `utils/reading/gen_config.py`),
   labelling its controls with the labels the scenes use
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