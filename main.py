from typing import List
import moderngl_window as mglw

from inputs.buttons import Button
from inputs.inputmanager import KeyboardManager
from params.params import Param
from params.valuecontrollers import CyclicController, RangedController


class Screen(mglw.WindowConfig):
    """Main application window that renders animated Julia fractals using OpenGL shaders"""
    
    # OpenGL configuration
    gl_version = (3, 3)
    title = "SynMix"
    window_size = (800, 800)
    aspect_ratio = None
    resizable = True
    resource_dir = 'shaders'  # Directory containing GLSL shader files

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load and compile vertex + fragment shaders into a single OpenGL program
        self.prog = self.load_program(
            vertex_shader="vertex.glsl",      # Handles fullscreen quad vertices
            fragment_shader="fract0.glsl",    # Computes Julia fractal for each pixel
        )

        # Current key being pressed (None when no key is pressed)
        self.key = None

        # Initialize input handling system
        self.inputmanager = KeyboardManager()
        self.params: List[Param]  # List of controllable parameters
        self.init_params()        # Create and bind parameters to keyboard inputs
        
        # Create a fullscreen quad geometry (2 triangles covering the entire screen)
        self.quad = mglw.geometry.quad_fs()

    def init_params(self):
        """Initialize controllable parameters and bind them to keyboard inputs"""
        self.params = []
        
        # X-axis offset control: Left/Right arrow keys, wraps around at boundaries
        self.params.append(Param(
            name="xOffset",                    # Corresponds to uniform in fragment shader
            button=Button.LEFT_WHEEL,          # Maps to Left/Right arrow keys
            controller=CyclicController(       # Values wrap around at min/max
                step=-0.001, min_value=-10.0, max_value=10.0)
        ))
        
        # Y-axis offset control: Up/Down arrow keys, wraps around at boundaries
        self.params.append(Param(
            name="yOffset",                    # Corresponds to uniform in fragment shader
            button=Button.RIGHT_WHEEL,         # Maps to Up/Down arrow keys
            controller=CyclicController(       # Values wrap around at min/max
                step=0.001, min_value=-10.0, max_value=10.0)
        ))
        
        # Color intensity control: Q/A keys, clamped at boundaries
        self.params.append(Param(
            name="colorFactor",                # Corresponds to uniform in fragment shader
            button=Button.RANGED_PLACEHOLDER,  # Maps to Q/A keys
            controller=RangedController(       # Values clamped at min/max
                step=0.01, min_value=0.0, max_value=1.0, initial_value=0.3)
        ))

        # Bind each parameter to the input manager for keyboard handling
        for param in self.params:
            self.inputmanager.bind_param(param)

    def handle_input(self):
        """Process keyboard input and update parameter values accordingly"""
        # Currently assuming keyboard input only (MIDI support planned for future)
        self.inputmanager.handle_input(key=self.key)

    def on_render(self, time: float, frame_time: float):
        """Main render loop - called every frame by moderngl-window"""
        # Process any pending keyboard input
        self.handle_input()

        # Update shader uniforms with current time and screen resolution
        self.prog['iTime'].value = time  # Used for fractal animation
        self.prog['iResolution'].value = (self.wnd.width, self.wnd.height, 1.0)
        
        # Update shader uniforms with current parameter values
        self.set_params_on_shader()

        # Clear the screen and render the fullscreen quad with fractal shader
        self.ctx.clear()
        self.quad.render(self.prog)  # Executes vertex + fragment shaders

    def set_params_on_shader(self):
        """Transfer parameter values to GPU shader uniforms"""
        for param in self.params:
            shader_param = self.prog[param.name]  # Get uniform by name
            org_value = shader_param.value
            shader_param.value = param.value      # Set new value
            
            # Debug output when parameter values change
            if org_value != param.value:
                print(f"Set {param.name} to {param.value}")

    def on_key_event(self, key, action, modifiers):
        """Handle keyboard events from moderngl-window"""
        if action == self.wnd.keys.ACTION_RELEASE:
            self.key = None  # No key pressed
        elif action == self.wnd.keys.ACTION_PRESS:
            self.key = key   # Store which key is currently pressed


if __name__ == "__main__":
    # Entry point: Create window and start the main rendering loop
    mglw.run_window_config(Screen)
