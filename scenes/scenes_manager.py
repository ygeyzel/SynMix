import tomllib
import json
from typing import Tuple
import random
from pprint import pprint

import moderngl_window as mglw
from pathlib import Path
from inputs.buttons import Button
from inputs.input_manager import MidiInputManager
from inputs.midi import MIDI_BUTTEN_CLICK, MIDI_DEC_VALUE, MIDI_INC_VALUE
from params.params import Param
from params.valuecontrollers import controllers_registry
from scenes.scene import Scene, update_shader_params_from_list
from top_level.global_context import DEFAULT_TIME_PARAMS, GlobalCtx, TimeParams


RESOURCES_DIR = Path('resources')
SCENES_DIR = RESOURCES_DIR / 'scenes'
SHADERS_DIR = RESOURCES_DIR / 'shaders'
SCENES_ORDER_FILE = RESOURCES_DIR / 'scenes_order.json'
POST_PROCESSING_PARAMS_FILE = SCENES_DIR / 'post_processing_params.toml'


TIME_OFFSET_STEP = 0.3
TIME_SPEED_STEP = 0.5
TIME_SPEED_HOLD_INTERVAL = 0.15


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
        self.global_ctx = GlobalCtx()
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

        self.time_offset_step = TIME_OFFSET_STEP
        self.time_speed_step = TIME_SPEED_STEP
        self._last_time = 0.0
        self._increase_speed_active = False
        self._decrease_speed_active = False
        self._increase_hold_accumulator = 0.0
        self._decrease_hold_accumulator = 0.0

    def init_general_funcs_bindings(self):
        binds = (
            (Button.RIGHT_LOAD, self.change_to_next_scene),
            (Button.LEFT_LOAD, self.change_to_previous_scene),
            (Button.SCROLL_CLICK, self.change_to_random_scene),
            (Button.SCROLL, self.adjust_time_offset),
            (Button.LEFT_MINUS, self.handle_decrease_speed_button),
            (Button.RIGHT_PLUS, self.handle_increase_speed_button),
        )

        for control_selector, afunc in binds:
            self.input_manager.bind_general_funcs(control_selector, afunc)

    def init_post_processing(self):
        """Initialize post-processing shader and FBO"""
        # Load post-processing shader
        vertex_path = SHADERS_DIR / 'vertex.glsl'
        fragment_path = SHADERS_DIR / 'post_processing.glsl'
        
        with open(vertex_path, 'r') as vf, open(fragment_path, 'r') as ff:
            vertex_source = vf.read()
            fragment_source = ff.read()
        
        # Create post-processing shader program
        self.post_prog = self.screen_ctx.program(vertex_shader=vertex_source,
                                                 fragment_shader=fragment_source)
        
        # Load post-processing parameters from dedicated file
        self.post_params = self._load_post_processing_params()
        
        # Bind post-processing parameters to secondary bindings
        for param in self.post_params:
            self.input_manager.bind_secondary_param(param)

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    @staticmethod
    def _generate_param_from_file_data(data):
        abuttom = Button.__members__[data['button']]
        controller_type = data['controller']['type']
        try:
            controller_cls, supported_button_types = controllers_registry[controller_type]
        except KeyError as exc:
            raise ValueError(
                f"Controller '{controller_type}' is not registered.") from exc

        if abuttom.button_type not in supported_button_types:
            supported_names = ', '.join(bt.name for bt in supported_button_types)
            raise ValueError(
                f"Controller '{controller_type}' supports button types {{{supported_names}}}, "
                f"but button '{abuttom.name}' is of type {abuttom.button_type.name}.")

        acontroller = controller_cls(**data['controller'].get('args', {}))
        return Param(name=data['name'], button=abuttom, controller=acontroller)

    def _load_scens_from_toml_files(self):
        for scene_file in SCENES_DIR.iterdir():
            if scene_file.name == POST_PROCESSING_PARAMS_FILE.name:
                continue
            if scene_file.suffix == '.toml':
                print(f'Loading scene from file: {scene_file.name}')
                with open(scene_file, 'rb') as f:
                    data = tomllib.load(f)

                data['params'] = [
                    self._generate_param_from_file_data(p) for p in data.get('params', [])
                ]
                ascene = Scene(**data)
                self.scenes.append(ascene)
                print(f'Scene {ascene.name} loaded')

        # Reorder scenes according to scenes_order.json
        self._reorder_scenes()

    def _load_post_processing_params(self):
        with open(POST_PROCESSING_PARAMS_FILE, 'rb') as f:
            data = tomllib.load(f)

        params_data = data.get('params', [])
        return [self._generate_param_from_file_data(p) for p in params_data]

    def _reorder_scenes(self):
        """Reorder scenes according to the order specified in scenes_order.json"""
        try:
            with open(SCENES_ORDER_FILE, 'r') as f:
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
            print(f'Warning: {SCENES_ORDER_FILE} not found. Using default order.')
        except (json.JSONDecodeError, KeyError) as e:
            print(
                f'Warning: Error parsing {SCENES_ORDER_FILE}: {e}. Using default order.')

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

        self._last_time = time

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
        self._apply_speed_hold(frame_time)
        
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
            adjusted_time = self._get_adjusted_time(time)
            self.current_prog['iTime'].value = adjusted_time

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

    def change_to_next_scene(self, value: int | None = None):
        if value is not None and value != MIDI_BUTTEN_CLICK:
            return
        self._new_scene_index = (
            self.current_scene_index + 1) % len(self.scenes)

    def change_to_previous_scene(self, value: int | None = None):
        if value is not None and value != MIDI_BUTTEN_CLICK:
            return
        self._new_scene_index = (
            self.current_scene_index - 1) % len(self.scenes)

    def change_to_random_scene(self, value: int | None = None):
        if value is not None and value != MIDI_BUTTEN_CLICK:
            return
        available_scenes = [
            scene for scene in self.scenes if scene != self.current_scene]
        if available_scenes:
            self._new_scene_index = self.scenes.index(
                random.choice(available_scenes))

    def load_new_scene(self):
        self.current_scene_index = self._new_scene_index
        new_csene = self.current_scene
        print(f'Change to scene {new_csene.name}')
        self.global_ctx.reset_time_params()

        # Reset all post-processing parameters to initial values
        for param in self.post_params:
            if param.is_reset_on_scene_change:
                param.controller.reset()

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
            if param.is_reset_on_scene_change:
                param.controller.reset()
            self.input_manager.bind_param(param)

    def adjust_time_offset(self, value: int | None):
        if value == MIDI_INC_VALUE:
            delta = self.time_offset_step
        elif value == MIDI_DEC_VALUE:
            delta = -self.time_offset_step
        else:
            return

        current = self.global_ctx.time_params or DEFAULT_TIME_PARAMS
        print(f'Update time offset to {current.offset + delta}')
        self._set_time_params(TimeParams(current.offset + delta, current.speed))

    def handle_increase_speed_button(self, value: int | None):
        is_pressed = value == MIDI_BUTTEN_CLICK
        self._increase_speed_active = is_pressed
        if not is_pressed:
            self._increase_hold_accumulator = 0.0
            return

        if is_pressed:
            self._update_time_speed(self.time_speed_step)

    def handle_decrease_speed_button(self, value: int | None):
        is_pressed = value == MIDI_BUTTEN_CLICK
        self._decrease_speed_active = is_pressed
        if not is_pressed:
            self._decrease_hold_accumulator = 0.0
            return

        self._update_time_speed(-self.time_speed_step)

    def _update_time_speed(self, delta: float):
        if delta == 0:
            return

        current = self.global_ctx.time_params or DEFAULT_TIME_PARAMS
        new_speed = max(-10.0, min(10.0, current.speed + delta))

        if new_speed == current.speed:
            return

        current_time = self._last_time if self._last_time is not None else 0.0
        new_offset = current.offset + current_time * (current.speed - new_speed)
        print(f'Update time speed to {new_speed}')
        self._set_time_params(TimeParams(new_offset, new_speed))

    def _set_time_params(self, new_params: TimeParams):
        self.global_ctx.time_params = new_params

    def _get_adjusted_time(self, base_time: float) -> float:
        params = self.global_ctx.time_params or DEFAULT_TIME_PARAMS
        return params.offset + (base_time * params.speed)

    def _apply_speed_hold(self, frame_time: float):
        if frame_time <= 0:
            return

        if self._increase_speed_active:
            self._increase_hold_accumulator += frame_time
            while self._increase_hold_accumulator >= TIME_SPEED_HOLD_INTERVAL:
                self._update_time_speed(self.time_speed_step)
                self._increase_hold_accumulator -= TIME_SPEED_HOLD_INTERVAL

        if self._decrease_speed_active:
            self._decrease_hold_accumulator += frame_time
            while self._decrease_hold_accumulator >= TIME_SPEED_HOLD_INTERVAL:
                self._update_time_speed(-self.time_speed_step)
                self._decrease_hold_accumulator -= TIME_SPEED_HOLD_INTERVAL
