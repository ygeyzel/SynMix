from typing import List
import moderngl_window as mglw

from inputs.inputmanager import KeyboardManager
from scenes.deadmau5_fractal import Deadmau5Fractal
from scenes.kepler_planet import KeplerPlanet
from scenes.scene import Scene


class Screen(mglw.WindowConfig):
    """Main application window - handles core window management and delegates rendering to scenes"""
    
    # OpenGL configuration
    gl_version = (3, 3)
    title = "SynMix"
    window_size = (800, 800)
    aspect_ratio = None
    resizable = True
    resource_dir = 'shaders'  # Directory containing GLSL shader files

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Current key being pressed (None when no key is pressed)
        self.key = None

        # Initialize input handling system
        self.inputmanager = KeyboardManager()
        
        # Initialize the scene (can be easily swapped for different scenes)
        # self.scene: Scene = Deadmau5Fractal(self.ctx, self.resource_dir)
        self.scene: Scene = KeplerPlanet(self.ctx, self.resource_dir)

        self.scene.setup()  # Load shaders, initialize parameters, create geometry
        
        # Bind scene parameters to input manager for keyboard handling
        for param in self.scene.params:
            self.inputmanager.bind_param(param)

    def handle_input(self):
        """Process keyboard input and update parameter values accordingly"""
        # Currently assuming keyboard input only (MIDI support planned for future)
        self.inputmanager.handle_input(key=self.key)

    def on_render(self, time: float, frame_time: float):
        """Main render loop - called every frame by moderngl-window"""
        # Process any pending keyboard input
        self.handle_input()

        # Delegate rendering to the current scene
        resolution = (self.wnd.width, self.wnd.height, 1.0)
        self.scene.render(time, frame_time, resolution)

    def on_key_event(self, key, action, modifiers):
        """Handle keyboard events from moderngl-window"""
        if action == self.wnd.keys.ACTION_RELEASE:
            self.key = None  # No key pressed
        elif action == self.wnd.keys.ACTION_PRESS:
            self.key = key   # Store which key is currently pressed


if __name__ == "__main__":
    # Entry point: Create window and start the main rendering loop
    mglw.run_window_config(Screen)
