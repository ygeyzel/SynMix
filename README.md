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
└── resources/           # Additional resources
```
