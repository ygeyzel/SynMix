import moderngl_window as mglw


class Screen(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "SynMix"
    window_size = (800, 800)
    aspect_ratio = None
    resizable = True
    resource_dir = 'shaders'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.load_program(
            vertex_shader="vertex.glsl",
            fragment_shader="fract0.glsl",
        )

        self.key = None
        self.quad = mglw.geometry.quad_fs()

    def on_render(self, time: float, frame_time: float):
        self.handle_pressed_key()

        self.prog['iTime'].value = time
        self.prog['iResolution'].value = (self.wnd.width, self.wnd.height, 1.0)

        self.ctx.clear()
        self.quad.render(self.prog)

    def handle_pressed_key(self):
        pass

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_RELEASE:
            self.key = None
        elif action == self.wnd.keys.ACTION_PRESS:
            self.key = key


if __name__ == "__main__":
    mglw.run_window_config(Screen)
