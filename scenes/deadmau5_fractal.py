from typing import List, Tuple
import moderngl_window as mglw

from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import CyclicController, NormalizedController
from scenes.scene import Scene


class Deadmau5Fractal(Scene):
    """Scene that renders animated Julia fractals - the original fractal implementation"""
    
    def get_shader_files(self) -> Tuple[str, str]:
        """Return the vertex and fragment shader filenames for the fractal scene"""
        return ("vertex.glsl", "fract0.glsl")
    
    def init_params(self) -> List[Param]:
        """Initialize controllable parameters for the fractal scene"""
        params = []
        
        # X-axis offset control: Left/Right arrow keys, wraps around at boundaries
        params.append(Param(
            name="xOffset",                    # Corresponds to uniform in fragment shader
            button=Button.LEFT_WHEEL,          # Maps to Left/Right arrow keys
            controller=CyclicController(       # Values wrap around at min/max
                step=0.001, min_value=-3.0, max_value=3.0)
        ))
        
        # Y-axis offset control: Up/Down arrow keys, wraps around at boundaries
        params.append(Param(
            name="yOffset",                    # Corresponds to uniform in fragment shader
            button=Button.RIGHT_WHEEL,         # Maps to Up/Down arrow keys
            controller=CyclicController(       # Values wrap around at min/max
                step=0.001, min_value=-3.0, max_value=3.0)
        ))
        
        # Color intensity control: Q/A keys, clamped at boundaries
        params.append(Param(
            name="colorFactor",                # Corresponds to uniform in fragment shader
            button=Button.LEFT_HIGH,  # Maps to Q/A keys
            controller=NormalizedController(       # Values clamped at min/max
                min_value=0.0, max_value=1.0, initial_value=0.3)
        ))
        
        return params
    
    def setup(self):
        """Complete scene setup - load shaders and initialize parameters"""
        super().setup()  # Load shaders and initialize parameters
        
        # Create a fullscreen quad geometry (2 triangles covering the entire screen)
        self.quad = mglw.geometry.quad_fs()
    
    def render(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Render the fractal scene
        
        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        # Update standard uniforms (time, resolution)
        self.update_uniforms(time, resolution)
        
        # Update parameter uniforms
        self.update_params()
        
        # Clear screen and render the fullscreen quad with fractal shader
        self.ctx.clear()
        self.quad.render(self.prog)  # Executes vertex + fragment shaders
