from typing import List, Tuple
import moderngl_window as mglw

from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import CyclicController, RangedController
from scenes.scene import Scene


class KeplerPlanet(Scene):
    """Scene that renders the Kepler 256o planetary visualization with dynamic controls"""
    
    def get_shader_files(self) -> Tuple[str, str]:
        """Return the vertex and fragment shader filenames for the Kepler scene"""
        return ("vertex.glsl", "kepler.glsl")
    
    def init_params(self) -> List[Param]:
        """Initialize controllable parameters for the Kepler planetary scene"""
        params = []
        
        # Orbit speed control: Left/Right wheel (arrow keys), affects planetary orbit speed
        params.append(Param(
            name="orbitSpeed",                 # Controls speed of planetary orbit animation
            button=Button.LEFT_WHEEL,          # Maps to Left/Right arrow keys
            controller=RangedController(       # Values clamped at min/max
                step=0.01, min_value=0.0, max_value=0.5, initial_value=0.125)
        ))
        
        # Time scale control: Up/Down wheel (arrow keys), affects overall animation speed
        params.append(Param(
            name="timeScale",                  # Controls overall time scaling
            button=Button.RIGHT_WHEEL,         # Maps to Up/Down arrow keys
            controller=RangedController(       # Values clamped at min/max
                step=0.005, min_value=0.0, max_value=0.3, initial_value=0.1)
        ))
        
        # Camera distance control: affects how close/far the camera is from the planet
        params.append(Param(
            name="cameraDistance",             # Controls camera distance from planet
            button=Button.RANGED_PLACEHOLDER,  # Maps to Q/A keys
            controller=RangedController(       # Values clamped at min/max
                step=0.1, min_value=1.5, max_value=5.0, initial_value=2.5)
        ))
        
        # Atmosphere intensity control: affects visibility of atmospheric effects
        params.append(Param(
            name="atmosphereIntensity",        # Controls atmosphere visibility
            button=Button.BUTTON_1,            # Maps to 1/2 keys
            controller=RangedController(       # Values clamped at min/max
                step=0.02, min_value=0.0, max_value=1.0, initial_value=0.45)
        ))
        
        # Cloud density control: affects cloud layer thickness
        params.append(Param(
            name="cloudDensity",               # Controls cloud density
            button=Button.BUTTON_2,            # Maps to 3/4 keys
            controller=RangedController(       # Values clamped at min/max
                step=0.1, min_value=0.0, max_value=8.0, initial_value=3.0)
        ))
        
        # Land contrast control: affects visibility of land masses
        params.append(Param(
            name="landContrast",               # Controls land visibility contrast
            button=Button.BUTTON_3,            # Maps to 5/6 keys
            controller=RangedController(       # Values clamped at min/max
                step=0.025, min_value=0.0, max_value=1.5, initial_value=0.75)
        ))
        
        # Star brightness control: affects star field visibility
        params.append(Param(
            name="starBrightness",             # Controls star field brightness
            button=Button.BUTTON_4,            # Maps to 7/8 keys
            controller=RangedController(       # Values clamped at min/max
                step=0.05, min_value=0.0, max_value=3.0, initial_value=1.0)
        ))
        
        # Surface detail control: affects terrain detail level
        params.append(Param(
            name="surfaceDetail",              # Controls surface detail level
            button=Button.BUTTON_5,            # Maps to 9/0 keys
            controller=RangedController(       # Values clamped at min/max
                step=0.05, min_value=0.1, max_value=2.0, initial_value=1.0)
        ))
        
        return params
    
    def setup(self):
        """Complete scene setup - load shaders and initialize parameters"""
        super().setup()  # Load shaders and initialize parameters
        
        # Create a fullscreen quad geometry (2 triangles covering the entire screen)
        self.quad = mglw.geometry.quad_fs()
    
    def render(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Render the Kepler planetary scene
        
        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        # Update standard uniforms (time, resolution)
        self.update_uniforms(time, resolution)
        
        # Update parameter uniforms
        self.update_params()
        
        # Clear screen and render the fullscreen quad with Kepler shader
        self.ctx.clear()
        self.quad.render(self.prog)  # Executes vertex + fragment shaders