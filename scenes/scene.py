from typing import List, Tuple
from pathlib import Path

from params.params import Param

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
        print(f'Loading shaders for scene "{self.name}":\n'
              f'  Vertex shader: {vertex_path}\n'
              f'  Fragment shader: {fragment_path}')
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
