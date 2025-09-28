from typing import List
import moderngl_window as mglw

from inputs.inputmanager import MidiInputManager
from scenes.deadmau5_fractal import Deadmau5Fractal
from scenes.kepler_planet import KeplerPlanet
from scenes.scene import Scene


MIDI_INPUT_SUBNAME = "Mixage"


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
        self.inputmanager = MidiInputManager(MIDI_INPUT_SUBNAME)
        
        # Initialize the scene (can be easily swapped for different scenes)
        self.scene: Scene = Deadmau5Fractal(self.ctx, self.resource_dir)
        # self.scene: Scene = KeplerPlanet(self.ctx, self.resource_dir)

        self.scene.setup()  # Load shaders, initialize parameters, create geometry
        
        # Bind scene parameters to input manager for keyboard handling
        for param in self.scene.params:
            self.inputmanager.bind_param(param, param.button.value)

    def on_render(self, time: float, frame_time: float):
        """Main render loop - called every frame by moderngl-window"""

        # Delegate rendering to the current scene
        resolution = (self.wnd.width, self.wnd.height, 1.0)
        self.scene.render(time, frame_time, resolution)


if __name__ == "__main__":
    # Entry point: Create window and start the main rendering loop
    mglw.run_window_config(Screen)
