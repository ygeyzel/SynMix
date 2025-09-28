import argparse
import sys
from typing import List
import moderngl_window as mglw

from inputs.inputmanager import MidiInputManager
from scenes.deadmau5_fractal import Deadmau5Fractal
from scenes.kepler_planet import KeplerPlanet
from scenes.scene import Scene
from utils.fakemidi import FakeMidi


MIDI_INPUT_SUBNAME = "Mixage"


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
    
    # Class variable to control whether to use FakeMidi
    use_fake_midi = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize input handling system
        self.fake_controller = FakeMidi() if self.use_fake_midi else None
        self.inputmanager: MidiInputManager
        self.init_input_manager()
        
        # Initialize the scene (can be easily swapped for different scenes)
        self.scene: Scene = Deadmau5Fractal(self.ctx, self.resource_dir)
        # self.scene: Scene = KeplerPlanet(self.ctx, self.resource_dir)

        self.scene.setup()  # Load shaders, initialize parameters, create geometry
        
        # Bind scene parameters to input manager for keyboard handling
        for param in self.scene.params:
            self.inputmanager.bind_param(param, param.button.value)

    def init_input_manager(self):
        input_subname = self.fake_controller.output_name if self.fake_controller else MIDI_INPUT_SUBNAME
        self.inputmanager = MidiInputManager(input_subname)

    def on_render(self, time: float, frame_time: float):
        """Main render loop - called every frame by moderngl-window"""

        # Process fake MIDI input if enabled
        if self.fake_controller:
            self.fake_controller.handle_keys_input()

        resolution = (self.wnd.width, self.wnd.height, 1.0)
        self.scene.render(time, frame_time, resolution)

    def on_key_event(self, key, action, modifiers):
        if self.fake_controller:
            if action == self.wnd.keys.ACTION_PRESS:
                self.fake_controller.on_key_press(key, modifiers)
            elif action == self.wnd.keys.ACTION_RELEASE:
                self.fake_controller.on_key_release(key)


if __name__ == "__main__":
    # Parse command line arguments (use parse_known_args to allow moderngl_window's args to pass through)
    parser = argparse.ArgumentParser(description='SynMix - Audio visualizer with MIDI control', add_help=False)
    parser.add_argument('--fakemidi', action='store_true', 
                        help='Use fake MIDI controller with keyboard input instead of real MIDI device')
    args, remaining = parser.parse_known_args()
    
    # Set class attribute based on argument
    Screen.use_fake_midi = args.fakemidi
    
    # Update sys.argv to remove our custom arguments so moderngl_window can parse its own
    sys.argv = [sys.argv[0]] + remaining
    
    # Entry point: Create window and start the main rendering loop
    mglw.run_window_config(Screen)
