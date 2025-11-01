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
    def __init__(self, screen_ctx, starting_scene_name: str = None):
        self.scenes = []
        self.input_manager = MidiInputManager()
        self.screen_ctx = screen_ctx
        self.current_prog = None
        self.quad = None
        self._load_scens_from_toml_files()
        assert len(self.scenes) > 0, "No scenes are loaded."

        self.init_general_funcs_bindings()
        self.current_scene_index = 0 if starting_scene_name is None else self.scenes.index(next(scene for scene in self.scenes if scene.name == starting_scene_name))
        self._new_scene_index = self.current_scene_index
        self.load_new_scene()
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
        
        # Reorder scenes according to scenes_order.json
        self._reorder_scenes()

    def _reorder_scenes(self):
        """Reorder scenes according to the order specified in scenes_order.json"""
        try:
            with open('config/scenes_order.json', 'r') as f:
                config = json.load(f)
            
            scene_order = config.get('scene_order', [])
            if not scene_order:
                return
            
            # Create a mapping of scene names to their indices in the desired order
            order_map = {name: idx for idx, name in enumerate(scene_order)}
            
            # Create a mapping of current scene names to Scene objects
            scenes_by_name = {scene.name: scene for scene in self.scenes}
            
            # Find scenes that are in the order list and sort them by order
            ordered_scenes = []
            for name in scene_order:
                if name in scenes_by_name:
                    ordered_scenes.append(scenes_by_name[name])
            
            # Add any scenes that weren't in the order list at the end
            for scene in self.scenes:
                if scene not in ordered_scenes:
                    ordered_scenes.append(scene)
            
            self.scenes = ordered_scenes
            print(f'Scenes reordered according to scenes_order.json')
            
        except FileNotFoundError:
            print('Warning: config/scenes_order.json not found. Using default order.')
        except (json.JSONDecodeError, KeyError) as e:
            print(f'Warning: Error parsing scenes_order.json: {e}. Using default order.')

    def render(self, time, frame_time, resolution):
        """
        Render the current scene

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self._new_scene_index is not None:
            self.load_new_scene()
            self._new_scene_index = None

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

        # Update shader parameters using the scene's method
        self.current_scene.update_shader_params(self.current_prog)

    def change_to_next_scene(self):
        self._new_scene_index = (self.current_scene_index + 1) % len(self.scenes)

    def change_to_previous_scene(self):
        self._new_scene_index = (self.current_scene_index - 1) % len(self.scenes)

    def change_to_random_scene(self):
        self._new_scene_index = self.scenes.index(random.choice(self.scenes))

    def load_new_scene(self):
        self.current_scene_index = self._new_scene_index
        new_csene = self.current_scene
        print(f'Change to scene {new_csene.name}')
        
        # Release old program if it exists
        if self.current_prog is not None:
            self.current_prog.release()
        
        # Load shader source code from the scene
        vertex_source, fragment_source = new_csene.get_shaders()
        
        # Create shader program
        self.current_prog = self.screen_ctx.program(vertex_shader=vertex_source,
                                                    fragment_shader=fragment_source)
        self.quad = mglw.geometry.quad_fs()
        
        # Bind parameters and track them for future cleanup
        self.input_manager.unbind_params()
        for param in new_csene.params:
            self.input_manager.bind_param(param)
