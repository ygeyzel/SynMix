# SynMix

SynMix is a real-time visual synthesis application that renders animated fractal graphics using OpenGL shaders. It's designed as an interactive visual instrument where parameters can be controlled in real-time through keyboard input, with plans for MIDI integration.

## Features

- **Real-time Fractal Rendering**: Displays animated Julia fractals with time-based animations
- **Interactive Parameter Control**: Live manipulation of visual parameters through keyboard input
- **Extensible Architecture**: Modular design supporting multiple input methods and parameter types
- **Live Visual Performance**: Designed for real-time visual performances and creative coding

## Current Controls

- **Arrow Keys (Left/Right)**: Control X offset of the fractal pattern
- **Arrow Keys (Up/Down)**: Control Y offset of the fractal pattern  
- **Q/A Keys**: Adjust color intensity factor

## Architecture

### Core Components
- **Visual Engine**: OpenGL shader pipeline with custom Julia fractal implementation
- **Parameter System**: Real-time controllable parameters mapped to shader uniforms
- **Input Management**: Keyboard input handling with framework for MIDI controller integration
- **Value Controllers**: Different parameter behavior types (ranged, cyclic)

### Technology Stack
- **Graphics**: ModernGL + ModernGL-Window for OpenGL rendering
- **Language**: Python 3.12
- **Dependency Management**: UV (modern Python package manager)
- **Shaders**: GLSL 3.3

## Installation

```bash
uv sync
```

## Run

```bash
uv run main.py
```

## Project Structure

```
├── main.py              # Main application entry point
├── inputs/              # Input handling system
│   ├── buttons.py       # Button mapping definitions
│   └── inputmanager.py  # Input event processing
├── params/              # Parameter control system
│   ├── params.py        # Parameter definitions
│   └── valuecontrollers.py # Parameter value controllers
├── shaders/             # GLSL shader files
│   ├── vertex.glsl      # Vertex shader
│   └── fract0.glsl      # Julia fractal fragment shader
└── resources/           # Additional resources
```

## Future Development

- MIDI controller integration for enhanced live performance capabilities
- Additional fractal algorithms and visual effects
- Parameter presets and automation
- Audio-reactive features
