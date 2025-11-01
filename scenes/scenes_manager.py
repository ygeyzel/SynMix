import tomllib
import json
from typing import List, Tuple
import os
import random
from pprint import pprint
import moderngl_window as mglw

from inputs.input_manager import MidiInputManager
from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import controllers_registry
from scenes.scene import Scene


class ScenesManager:
    # Static dictionary mapping scene names to their indices
    SCENE_INDEX_MAP = {}

    def __init__(self, screen_ctx):
        self.scenes = []
        self.input_manager = MidiInputManager()
        self.screen_ctx = screen_ctx
        self.current_prog = None
        self.quad = None
        self._load_scens_from_toml_files()
        assert len(self.scenes) > 0, "No scenes are loaded."
        self._build_scene_index_map()
        self.init_general_funcs_bindings()
        self.current_scene_index = 0
        self.load_scene()
        self.start_time = None
        pprint(self.scenes)

    def init_general_funcs_bindings(self):
        binds = ((Button.RIGHT_LOAD, self.change_to_next_scene),
                 (Button.LEFT_LOAD, self.change_to_previous_scene),
                 (Button.SCROLL_CLICK, self.change_to_random_scene))

        for control_selector, afunc in binds:
            self.input_manager.bind_general_funcs(control_selector, afunc)

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    def _build_scene_index_map(self):
        """Build a mapping from scene names to their indices"""
        ScenesManager.SCENE_INDEX_MAP = {scene.name: idx for idx, scene in enumerate(self.scenes)}

    @staticmethod
    def _generat_param_from_file_data(data):
        abuttom = Button.__members__[data['button']]
        acontroller = controllers_registry[data['controller']['type']](**data['controller']['args'])
        return Param(name=data['name'], button=abuttom, controller=acontroller)

    def _load_scens_from_toml_files(self):
        for afile in os.listdir('scenes'):
            if afile.endswith('.toml'):
                with open(f'scenes/{afile}', 'rb') as f:
                    data = tomllib.load(f)

                data['params'] = [self._generat_param_from_file_data(p) for p in data['params']]
                ascene = Scene(**data)
                self.scenes.append(ascene)
                print(f'Scene {ascene.name} loaded')

    def render(self, time, frame_time, resolution):
        """
        Render the current scene

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        self._update_params(time, frame_time, resolution)
        self.screen_ctx.clear()
        self.quad.render(self.current_prog)  # Executes vertex + fragment shaders

    def _update_params(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Update shader uniforms with current parameter values

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self.current_prog is None:
            return

        if 'iTime' in self.current_prog:
            self.current_prog['iTime'].value = time

        if 'iResolution' in self.current_prog:
            self.current_prog['iResolution'].value = resolution

        _ = frame_time # for future use

        for param in self.current_scene.params:
            if param.name in self.current_prog:
                shader_param = self.current_prog[param.name]
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

    def change_to_next_scene(self):
        self.current_scene_index = (self.current_scene_index + 1) % len(self.scenes)
        self.load_scene()

    def change_to_previous_scene(self):
        self.current_scene_index = (self.current_scene_index - 1) % len(self.scenes)
        self.load_scene()

    def change_to_random_scene(self):
        self.current_scene_index = self.scenes.index(random.choice(self.scenes))
        self.load_scene()

    def change_to_scene_by_name(self, name: str):
        for idx, scene in enumerate(self.scenes):
            if name == scene.name:
                self.current_scene_index = idx
                self.load_scene()
                break

        else:
            raise ValueError(f'no scene named:\'{name}\' in {[s.name for s in self.scenes]}')

    def load_scene(self):
        new_csene = self.current_scene
        print(f'Change to scene {new_csene.name}')
        # Load shader source code from the scene
        vertex_source, fragment_source = new_csene.get_shaders()
        # Create shader program
        self.current_prog = self.screen_ctx.program(vertex_shader=vertex_source,
                                                    fragment_shader=fragment_source)
        self.quad = mglw.geometry.quad_fs()
        # Bind parameters
        for param in new_csene.params:
            self.input_manager.bind_param(param)

