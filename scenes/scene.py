from typing import List, Tuple
from pathlib import Path

from params.params import Param


def _values_changed(org_value, new_value):
    """
    Check if two values are significantly different
    
    Args:
        org_value: Original value
        new_value: New value
        
    Returns:
        True if values have changed, False otherwise
    """
    values_changed = False
    try:
        # For numeric types (float, int)
        if isinstance(org_value, (int, float)) and isinstance(new_value, (int, float)):
            values_changed = abs(org_value - new_value) > 1e-6

        # For sequences (vectors, tuples, lists)
        elif hasattr(org_value, '__len__') and hasattr(new_value, '__len__'):
            if len(org_value) == len(new_value):
                values_changed = any(abs(a - b) > 1e-6 for a, b in zip(org_value, new_value))
            else:
                values_changed = True

        # For other types, use direct comparison
        else:
            values_changed = (org_value != new_value)

    except (TypeError, AttributeError):
        # Fallback to direct comparison if numeric operations fail
        values_changed = org_value != new_value
    
    return values_changed


def update_shader_params_from_list(shader_program, params):
    """
    Update shader uniforms with current parameter values from a list of params
    
    Args:
        shader_program: The shader program to update
        params: List of Param objects to update
    """
    if shader_program is None:
        return
    
    for param in params:
        if param.name in shader_program:
            shader_param = shader_program[param.name]
            org_value = shader_param.value
            shader_param.value = param.value

            # Debug output when parameter values change
            if _values_changed(org_value, param.value):
                print(f"Set {param.name} to {param.value}")

SHADERS_DIR = 'shaders'


class Scene:
    """A class for common shader based visual scene functionality"""

    def __init__(self, name: str, params: List[Param], fragment_shader_filename: str, vertex_shader_filename: str = 'vertex.glsl'):
        self.name = name
        self.params = params
        self.fragment_shader_filename = fragment_shader_filename
        self.vertex_shader_filename = vertex_shader_filename

    def __repr__(self):
        return f'Scene({self.name}: shaders=[{self.fragment_shader_filename},{self.vertex_shader_filename}], params:{[p for p in self.params]})'

    def __str__(self):
        return self.__repr__()

    def get_shaders(self) -> Tuple[str, str]:
        """
        Load and return shader source code from files

        Returns:
            Tuple of (vertex_shader_source, fragment_shader_source)
        """
        vertex_path = Path(SHADERS_DIR) / self.vertex_shader_filename
        fragment_path = Path(SHADERS_DIR) / self.fragment_shader_filename

        try:
            with open(vertex_path, 'r') as vf, open(fragment_path, 'r') as ff:
                vertex_source = vf.read()
                fragment_source = ff.read()
                return vertex_source, fragment_source

        except OSError as e:
            raise RuntimeError(f'Failed to load shader files:\n'
                               f"  Vertex shader: {vertex_path}\n"
                               f"  Fragment shader: {fragment_path}\n"
                               f"Error: {e}") from e

    def update_shader_params(self, shader_program):
        """
        Update shader uniforms with current parameter values
        
        Args:
            shader_program: The shader program to update
        """
        update_shader_params_from_list(shader_program, self.params)
