from abc import ABC, abstractmethod
from typing import List, Tuple
import moderngl_window as mglw

from params.params import Param


class Scene(ABC):
    """Abstract base class for visual scenes that can be rendered with shaders"""
    
    def __init__(self, ctx, resource_dir: str = 'shaders'):
        """
        Initialize the scene with OpenGL context and resource directory
        
        Args:
            ctx: ModernGL context for OpenGL operations
            resource_dir: Directory containing shader files
        """
        self.ctx = ctx
        self.resource_dir = resource_dir
        self.prog = None  # OpenGL shader program
        self.params: List[Param] = []  # Controllable parameters
        
    @abstractmethod
    def get_shader_files(self) -> Tuple[str, str]:
        """
        Return the vertex and fragment shader filenames for this scene
        
        Returns:
            Tuple of (vertex_shader_filename, fragment_shader_filename)
        """
        pass
    
    @abstractmethod
    def init_params(self) -> List[Param]:
        """
        Initialize and return the list of controllable parameters for this scene
        
        Returns:
            List of Param objects that can be controlled via input
        """
        pass
    
    def load_shaders(self):
        """Load and compile the shader program for this scene"""
        vertex_shader, fragment_shader = self.get_shader_files()
        
        # Read shader files directly from the resource directory
        import os
        vertex_path = os.path.join(self.resource_dir, vertex_shader)
        fragment_path = os.path.join(self.resource_dir, fragment_shader)
        
        try:
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
        except OSError as e:
            raise RuntimeError(
                f"Failed to load shader files:\n"
                f"  Vertex shader: {vertex_path}\n"
                f"  Fragment shader: {fragment_path}\n"
                f"Error: {e}"
            ) from e
        
        self.prog = self.ctx.program(
            vertex_shader=vertex_source,
            fragment_shader=fragment_source
        )
    
    def setup(self):
        """Complete scene setup - load shaders and initialize parameters"""
        self.load_shaders()
        self.params = self.init_params()
    
    def update_uniforms(self, time: float, resolution: Tuple[float, float, float]):
        """
        Update standard shader uniforms that most scenes will need
        
        Args:
            time: Current time for animations
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if 'iTime' in self.prog:
            self.prog['iTime'].value = time
        if 'iResolution' in self.prog:
            self.prog['iResolution'].value = resolution
    
    def update_params(self):
        """Update shader uniforms with current parameter values"""
        for param in self.params:
            if param.name in self.prog:
                shader_param = self.prog[param.name]
                org_value = shader_param.value
                shader_param.value = param.value
                
                # Debug output when parameter values change (with tolerance for float comparison)
                if abs(org_value - param.value) > 1e-6:
                    print(f"[{self.__class__.__name__}] Set {param.name} to {param.value}")
    
    @abstractmethod
    def render(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Render the scene
        
        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        pass