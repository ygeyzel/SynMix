
import moderngl_window as mglw
from scenes.scenes_manager import ScenesManager
from inputs.input_manager import MidiInputManager
from utils.fakemidi import FakeMidi 


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fake_midi = FakeMidi.get_fake_midi_if_exist()
        self.sm = ScenesManager(self.ctx)


    def on_render(self, time: float, frame_time: float):
        """Main render loop - called every frame by moderngl-window"""

        if self.fake_midi:
            self.fake_midi.handle_keys_input()

        # Delegate rendering to the current scene
        resolution = (self.wnd.width, self.wnd.height, 1.0)
        # self.scene.render(time, frame_time, resolution)
        self.sm.render(time, frame_time, resolution)

    def on_key_event(self, key, action, modifiers):
        if self.fake_midi:
            if action == self.wnd.keys.ACTION_PRESS:
                self.fake_midi.on_key_press(key, modifiers)

            elif action == self.wnd.keys.ACTION_RELEASE:
                self.fake_midi.on_key_release(key)



