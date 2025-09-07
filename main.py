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
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.color_factor = 0.3
        self.quad = mglw.geometry.quad_fs()

    def on_render(self, time: float, frame_time: float):
        self.handle_pressed_key()

        self.prog['iTime'].value = time
        self.prog['iResolution'].value = (self.wnd.width, self.wnd.height, 1.0)
        self.prog['colorFactor'].value = self.color_factor
        self.prog['xOffset'].value = self.x_offset
        self.prog['yOffset'].value = self.y_offset

        self.ctx.clear()
        self.quad.render(self.prog)

    def handle_pressed_key(self):
        if self.key == self.wnd.keys.UP:
            self.x_offset += 0.001
        elif self.key == self.wnd.keys.DOWN:
            self.x_offset -= 0.001

        if self.key == self.wnd.keys.RIGHT:
            self.y_offset += 0.001
        elif self.key == self.wnd.keys.LEFT:
            self.y_offset -= 0.001

        if self.key == self.wnd.keys.Q:
            self.color_factor += 0.01
        elif self.key == self.wnd.keys.A:
            self.color_factor -= 0.01

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_RELEASE:
            self.key = None
        elif action == self.wnd.keys.ACTION_PRESS:
            self.key = key


if __name__ == "__main__":
    mglw.run_window_config(Screen)
