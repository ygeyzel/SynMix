import moderngl_window as mglw

from synmix.fakemidi.fakemidi import FakeMidi
from synmix.inputs.input_manager import MidiInputManager
from synmix.resource_loader import get_shaders_dir
from synmix.scenes.scenes_manager import ScenesManager
from synmix.top_level.global_context import GlobalCtx

MIDI_INPUT_SUBNAME = "Mixage"


class Screen(mglw.WindowConfig):
    """Main application window - handles core window management and delegates rendering to scenes."""

    # OpenGL configuration
    gl_version = (3, 3)
    title = "SynMix"
    window_size = (800, 800)
    aspect_ratio = None
    resizable = True
    resource_dir = str(get_shaders_dir())  # Directory containing GLSL shader files

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        global_ctx = GlobalCtx()

        if self.argv.fakemidi:
            global_ctx.fake_midi = FakeMidi()

        if self.argv.start_scene:
            global_ctx.starting_scene_name = self.argv.start_scene

        self.fake_midi = global_ctx.fake_midi
        input_subname = (
            self.fake_midi.output_name if self.fake_midi else MIDI_INPUT_SUBNAME
        )
        _input_manager = MidiInputManager(input_subname)

        self.sm = ScenesManager(
            self.ctx, starting_scene_name=global_ctx.starting_scene_name
        )
        self.input_manager = MidiInputManager()

    def on_render(self, time: float, frame_time: float) -> None:
        """Main render loop - called every frame by moderngl-window."""
        if self.fake_midi:
            self.fake_midi.handle_keys_input()
            # Process pending messages on Windows
            self.input_manager.process_fake_midi_messages()

        # Delegate rendering to the current scene
        resolution = (self.wnd.width, self.wnd.height, 1.0)
        # self.scene.render(time, frame_time, resolution)
        self.sm.render(time, frame_time, resolution)

    def on_key_event(self, key, action, modifiers) -> None:
        if self.fake_midi:
            if action == self.wnd.keys.ACTION_PRESS:
                self.fake_midi.on_key_press(key, modifiers)

            elif action == self.wnd.keys.ACTION_RELEASE:
                self.fake_midi.on_key_release(key)

    @classmethod
    def add_arguments(cls, parser):
        parser.description = "SynMix - Audio visualizer with MIDI control"
        parser.add_argument(
            "--fakemidi",
            action="store_true",
            help="Use fake MIDI controller with keyboard input instead of real MIDI device",
        )
        parser.add_argument(
            "--start-scene", type=str, default=None, help="Name of the starting scene"
        )
