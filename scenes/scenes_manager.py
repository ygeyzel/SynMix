import tomllib
import json
from typing import Tuple
import os
import random
from pprint import pprint

import moderngl_window as mglw
from pathlib import Path
from inputs.input_manager import MidiInputManager
from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import controllers_registry, ToggleController, IsPressedController
from scenes.scene import Scene, update_shader_params_from_list


class ScenesManager:
    def __init__(self, screen_ctx, starting_scene_name: str = None):
        self.scenes = []
        self.input_manager = MidiInputManager()
        self.screen_ctx = screen_ctx
        self.current_prog = None
        self.post_prog = None
        self.quad = None
        self.fbo = None
        self.fbo_texture = None
        self._load_scens_from_toml_files()
        assert len(self.scenes) > 0, "No scenes are loaded."

        self.init_general_funcs_bindings()
        self.init_post_processing()
        self.current_scene_index = 0 if starting_scene_name is None else self.scenes.index(
            next(scene for scene in self.scenes if scene.name == starting_scene_name))
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

    def init_post_processing(self):
        """Initialize post-processing shader and FBO"""
        # Load post-processing shader
        vertex_path = Path('shaders') / 'vertex.glsl'
        fragment_path = Path('shaders') / 'post_processing.glsl'
        
        with open(vertex_path, 'r') as vf, open(fragment_path, 'r') as ff:
            vertex_source = vf.read()
            fragment_source = ff.read()
        
        # Create post-processing shader program
        self.post_prog = self.screen_ctx.program(vertex_shader=vertex_source,
                                                 fragment_shader=fragment_source)
        
        # Initialize post-processing parameters
        self.post_params = []
        # Color inversion parameter
        invert_param = Param(
            name='uInvertColors',
            button=Button.LEFT_CUE_1,
            controller=ToggleController()
        )
        self.post_params.append(invert_param)
        
        # Wave effect parameter
        waves_x_param = Param(
            name='uWavesX',
            button=Button.LEFT_MINUS,
            controller=IsPressedController()
        )
        self.post_params.append(waves_x_param)

        wave_y_param = Param(
            name='uWavesY',
            button=Button.LEFT_PLUS,
            controller=IsPressedController()
        )
        self.post_params.append(wave_y_param)
        
        # Bind post-processing parameters to secondary bindings
        for param in self.post_params:
            self.input_manager.bind_secondary_param(param)

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    @staticmethod
    def _generat_param_from_file_data(data):
        abuttom = Button.__members__[data['button']]
        acontroller = controllers_registry[data['controller']['type']](
            **data['controller']['args'])
        return Param(name=data['name'], button=abuttom, controller=acontroller)

    def _load_scens_from_toml_files(self):
        for afile in os.listdir('scenes'):
            if afile.endswith('.toml'):
                with open(f'scenes/{afile}', 'rb') as f:
                    data = tomllib.load(f)

                data['params'] = [self._generat_param_from_file_data(
                    p) for p in data['params']]
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
            print(
                f'Warning: Error parsing scenes_order.json: {e}. Using default order.')

    def render(self, time, frame_time, resolution):
        """
        Render the current scene with 2-pass rendering

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self._new_scene_index is not None:
            self.load_new_scene()
            self._new_scene_index = None

        width, height = int(resolution[0]), int(resolution[1])
        
        # Resize FBO if needed
        if self.fbo is None or self.fbo_texture.width != width or self.fbo_texture.height != height:
            if self.fbo is not None:
                self.fbo.release()
            self.fbo_texture = self.screen_ctx.texture((width, height), 4)
            self.fbo_texture.filter = (self.screen_ctx.LINEAR, self.screen_ctx.LINEAR)
            self.fbo = self.screen_ctx.framebuffer([self.fbo_texture])
        
        # Update parameters for both passes
        self._update_params(time, frame_time, resolution)
        self._update_post_params(time, frame_time, resolution)
        
        # FIRST PASS: Render scene to FBO
        self.fbo.use()
        self.fbo.clear()
        self.quad.render(self.current_prog)
        
        # SECOND PASS: Render FBO texture to screen with post-processing
        self.screen_ctx.screen.use()
        self.screen_ctx.clear()
        self.fbo_texture.use(0)
        self.quad.render(self.post_prog)

    def _update_params(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Update shader uniforms with current parameter values for first pass

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

        _ = frame_time  # for future use

        # Update shader parameters using the scene's method
        self.current_scene.update_shader_params(self.current_prog)

    def _update_post_params(self, time: float, frame_time: float, resolution: Tuple[float, float, float]):
        """
        Update shader uniforms with current parameter values for second pass

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self.post_prog is None:
            return

        if 'iResolution' in self.post_prog:
            self.post_prog['iResolution'].value = resolution

        if 'iTime' in self.post_prog:
            self.post_prog['iTime'].value = time

        # Update post-processing shader parameters
        update_shader_params_from_list(self.post_prog, self.post_params)

    def change_to_next_scene(self):
        self._new_scene_index = (
            self.current_scene_index + 1) % len(self.scenes)

    def change_to_previous_scene(self):
        self._new_scene_index = (
            self.current_scene_index - 1) % len(self.scenes)

    def change_to_random_scene(self):
        available_scenes = [
            scene for scene in self.scenes if scene != self.current_scene]
        if available_scenes:
            self._new_scene_index = self.scenes.index(
                random.choice(available_scenes))

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
