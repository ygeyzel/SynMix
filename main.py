from typing import List
import moderngl_window as mglw

from inputs.buttons import Button
from inputs.inputmanager import KeyboardManager
from params.params import Param
from params.valuecontrollers import CyclicController, RangedController


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

        self.inputmanager = KeyboardManager()
        self.params: List[Param]
        self.init_params()
        self.quad = mglw.geometry.quad_fs()

    def init_params(self):
        self.params = []
        self.params.append(Param(
            name="xOffset",
            button=Button.LEFT_WHEEL,
            controller=CyclicController(
                step=-0.001, min_value=-10.0, max_value=10.0)
        ))
        self.params.append(Param(
            name="yOffset",
            button=Button.RIGHT_WHEEL,
            controller=CyclicController(
                step=0.001, min_value=-10.0, max_value=10.0)
        ))
        self.params.append(Param(
            name="colorFactor",
            button=Button.RANGED_PLACEHOLDER,
            controller=RangedController(
                step=0.01, min_value=0.0, max_value=1.0, initial_value=0.3)
        ))

        for param in self.params:
            self.inputmanager.bind_param(param)

    def handle_input(self):
        # currenly assuming keyboard input only
        self.inputmanager.handle_input(key=self.key)

    def on_render(self, time: float, frame_time: float):
        self.handle_input()

        self.prog['iTime'].value = time
        self.prog['iResolution'].value = (self.wnd.width, self.wnd.height, 1.0)
        self.set_params_on_shader()

        self.ctx.clear()
        self.quad.render(self.prog)

    def set_params_on_shader(self):
        for param in self.params:
            shader_param = self.prog[param.name]
            org_value = shader_param.value
            shader_param.value = param.value

            if org_value != param.value:
                print(f"Set {param.name} to {param.value}")

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_RELEASE:
            self.key = None
        elif action == self.wnd.keys.ACTION_PRESS:
            self.key = key


if __name__ == "__main__":
    mglw.run_window_config(Screen)
