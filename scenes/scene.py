from abc import ABC, abstractmethod
from typing import List, Tuple
import moderngl_window as mglw
from pathlib import Path
import os

from params.params import Param

SHADERS_DIR = 'shaders'

class Scene:
    """A class for common shader based visual scene functionality"""

    def __init__(self, name: str, params: List[Param], fragment_shader_filename: str, vertex_shader_filename: str = 'vertex.glsl'):
        self.name = name
        self.params = params
        self.fragment_shader_filename = fragment_shader_filename
        self.vertex_shader_filename = vertex_shader_filename
        self.screen_ctx = None
        self.prog = None

    def __repr__(self):
        return f'Scene({self.name}: shaders=[{self.fragment_shader_filename},{self.vertex_shader_filename}], params:{[p for p in self.params]})'

    def __str__(self):
        return self.__repr__()

    def _load_shaders_code_from_files(self, screen_ctx):
        vertex_path = Path(SHADERS_DIR) / self.vertex_shader_filename
        fragment_path = Path(SHADERS_DIR) / self.fragment_shader_filename
        try:
            with open(vertex_path, 'r') as vf, open(fragment_path, 'r') as ff:
                vertex_source = vf.read()
                fragment_source = ff.read()

        except OSError as e:
            raise RuntimeError(f'Failed to load shader files:\n'
                               f"  Vertex shader: {vertex_path}\n"
                               f"  Fragment shader: {fragment_path}\n"
                               f"Error: {e}") from e

        self.prog = screen_ctx.program(vertex_shader=vertex_source,
                                       fragment_shader=fragment_source)


    def setup(self, screen_ctx):
        """Load and compile the shader program for this scene"""
        self._load_shaders_code_from_files(screen_ctx)
        self.screen_ctx = screen_ctx
        self.quad = mglw.geometry.quad_fs()

    def update_params(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Update shader uniforms with current parameter values

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self.prog is None:
            print('get self.prog is  None')
            return

        if 'iTime' in self.prog:
            self.prog['iTime'].value = time

        if 'iResolution' in self.prog:
            self.prog['iResolution'].value = resolution

        _ = frame_time # for future use

        for param in self.params:
            if param.name in self.prog:
                shader_param = self.prog[param.name]
                org_value = shader_param.value
                shader_param.value = param.value

                # Debug output when parameter values change
                # Handle different uniform types safely
                values_changed = False
                try:
                    # For numeric types (float, int)
                    if isinstance(org_value, (int, float)) and isinstance(param.value, (int, float)):
                        values_changed = abs(org_value - param.value) > 1e-6

                    # For sequences (vectors, tuples, lists)
                    elif hasattr(org_value, '__len__') and hasattr(param.value, '__len__'):
                        if len(org_value) == len(param.value):
                            values_changed = any(abs(a - b) > 1e-6 for a, b in zip(org_value, param.value))

                        else:
                            values_changed = True

                    # For other types, use direct comparison
                    else:
                        values_changed = (org_value != param.value)

                except (TypeError, AttributeError):
                    # Fallback to direct comparison if numeric operations fail
                    values_changed = org_value != param.value

                if values_changed:
                    print(f"[{self.__class__.__name__}] Set {param.name} to {param.value}")

    def render(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Render the scene

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """ 
        self.update_params(time, frame_time, resolution)
        if self.screen_ctx is None:
            print('got self.screen_ctx is None')
            return
        self.screen_ctx.clear()
        self.quad.render(self.prog)  # Executes vertex + fragment shaders
