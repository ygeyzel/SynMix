from typing import Optional

import moderngl_window as mglw
from global_context import GlobalCtx
from scenes.scenes_manager import ScenesManager


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

        global_ctx = GlobalCtx()
        self.fake_midi = global_ctx.fake_midi
        self.sm = ScenesManager(self.ctx, starting_scene_name=global_ctx.starting_scene_name)

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

