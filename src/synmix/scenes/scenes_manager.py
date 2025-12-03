import tomllib
import json
from typing import Tuple, Dict
import random
from pprint import pprint

import moderngl_window as mglw
from pathlib import Path
from synmix.inputs.buttons import Button
from synmix.inputs.input_manager import MidiInputManager
from synmix.inputs.midi import MIDI_BUTTEN_CLICK
from synmix.params.params import Param
from synmix.params.valuecontrollers import controllers_registry
from synmix.scenes.scene import Scene, update_shader_params_from_list
from synmix.top_level.global_context import GlobalCtx
from synmix.resource_loader import (
    get_scenes_dir,
    get_shaders_dir,
    get_textures_dir,
    get_scenes_order_file,
    get_post_processing_params_file,
)

try:
    from PIL import Image
    import numpy as np

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


SCENES_DIR = get_scenes_dir()
SHADERS_DIR = get_shaders_dir()
TEXTURES_DIR = get_textures_dir()
SCENES_ORDER_FILE = get_scenes_order_file()
POST_PROCESSING_PARAMS_FILE = get_post_processing_params_file()


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
        self.textures: Dict[str, any] = {}  # Store loaded textures
        self._load_scens_from_toml_files()
        assert len(self.scenes) > 0, "No scenes are loaded."

        self.init_general_funcs_bindings()
        self.init_post_processing()
        self.current_scene_index = (
            0
            if starting_scene_name is None
            else self.scenes.index(
                next(
                    scene for scene in self.scenes if scene.name == starting_scene_name
                )
            )
        )
        pprint(self.scenes)
        self._new_scene_index = (
            self.current_scene_index
        )  # triggers self.load_new_scene()
        self.start_time = None

    def init_general_funcs_bindings(self):
        binds = (
            (Button.RIGHT_LOAD, self.change_to_next_scene),
            (Button.LEFT_LOAD, self.change_to_previous_scene),
            (Button.SCROLL_CLICK, self.change_to_random_scene),
            (Button.SCROLL, self.global_ctx.adjust_time_offset),
            (Button.LEFT_MINUS, self.global_ctx.handle_decrease_speed_button),
            (Button.RIGHT_MINUS, self.global_ctx.handle_decrease_speed_button),
            (Button.RIGHT_PLUS, self.global_ctx.handle_increase_speed_button),
            (Button.LEFT_PLUS, self.global_ctx.handle_increase_speed_button),
        )

        for control_selector, afunc in binds:
            self.input_manager.bind_general_funcs(control_selector, afunc)

    def _load_textures(self):
        """Load all images from resources/textures directory as textures"""
        if not PIL_AVAILABLE:
            print("Warning: PIL/Pillow not available. Textures will not be loaded.")
            print("Install Pillow with: pip install Pillow")
            return

        if not TEXTURES_DIR.exists():
            print(f"Warning: Textures directory {TEXTURES_DIR} does not exist.")
            return

        # Supported image formats
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tga", ".gif"}

        for texture_file in TEXTURES_DIR.iterdir():
            if texture_file.suffix.lower() in image_extensions:
                try:
                    # Load image with PIL
                    if not PIL_AVAILABLE:
                        continue
                    # Type checker: Image and np are available when PIL_AVAILABLE is True
                    assert Image is not None and np is not None, (
                        "PIL modules should be available"
                    )  # type: ignore
                    img = Image.open(texture_file).convert("RGB")  # type: ignore
                    img_data = np.array(img)  # type: ignore

                    # Create texture from image data
                    texture = self.screen_ctx.texture(img.size, 3, img_data.tobytes())
                    texture.filter = (self.screen_ctx.LINEAR, self.screen_ctx.LINEAR)
                    texture.build_mipmaps()

                    # Store texture with filename (without extension) as key
                    texture_name = texture_file.stem
                    self.textures[texture_name] = texture
                    print(f"Loaded texture: {texture_name} from {texture_file.name}")

                except Exception as e:
                    print(f"Error loading texture {texture_file.name}: {e}")

    def init_post_processing(self):
        """Initialize post-processing shader and FBO"""
        # Load textures first
        self._load_textures()

        # Load post-processing shader
        vertex_path = SHADERS_DIR / "vertex.glsl"
        fragment_path = SHADERS_DIR / "post_processing.glsl"

        with open(vertex_path, "r") as vf, open(fragment_path, "r") as ff:
            vertex_source = vf.read()
            fragment_source = ff.read()

        # Create post-processing shader program
        self.post_prog = self.screen_ctx.program(
            vertex_shader=vertex_source, fragment_shader=fragment_source
        )

        # Bind textures to shader uniforms (uniforms must be declared in shader)
        self._bind_textures_to_shader()

        # Load post-processing parameters from dedicated file
        self.post_params = self._load_post_processing_params()

        # Bind post-processing parameters to secondary bindings
        for param in self.post_params:
            self.input_manager.bind_secondary_param(param)

    def _bind_textures_to_shader(self):
        """Bind loaded textures to post-processing shader uniforms.

        Textures are bound to uniforms that are manually declared in the shader.
        The method tries to match texture names to uniform names using common conventions:
        - uTexture_<texture_name>
        - <texture_name>
        """
        if not self.textures or not self.post_prog:
            return

        # Bind textures to texture units starting from 1 (0 is reserved for uTexture)
        texture_unit = 1
        for texture_name, texture in self.textures.items():
            # Clean the texture name for uniform matching
            clean_name = texture_name.replace("-", "_").replace(" ", "_")

            # Try different uniform name conventions
            uniform_candidates = [
                f"uTexture_{clean_name}",  # uTexture_tv_error
                clean_name,  # tv_error
            ]

            bound = False
            for uniform_name in uniform_candidates:
                if uniform_name in self.post_prog:
                    texture.use(texture_unit)
                    self.post_prog[uniform_name].value = texture_unit
                    texture_unit += 1
                    bound = True
                    break

            if not bound:
                print(
                    f"Warning: Texture '{texture_name}' loaded but no matching uniform found in shader. "
                    f"Declare a uniform like 'uniform sampler2D uTexture_{clean_name};' in the shader."
                )

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    @staticmethod
    def _generate_param_from_file_data(data):
        abuttom = Button.__members__[data["button"]]
        controller_type = data["controller"]["type"]
        try:
            controller_cls, supported_button_types = controllers_registry[
                controller_type
            ]
        except KeyError as exc:
            raise ValueError(
                f"Controller '{controller_type}' is not registered."
            ) from exc

        if abuttom.button_type not in supported_button_types:
            supported_names = ", ".join(bt.name for bt in supported_button_types)
            raise ValueError(
                f"Controller '{controller_type}' supports button types {{{supported_names}}}, "
                f"but button '{abuttom.name}' is of type {abuttom.button_type.name}."
            )

        acontroller = controller_cls(**data["controller"].get("args", {}))
        return Param(name=data["name"], button=abuttom, controller=acontroller)

    def _load_scens_from_toml_files(self):
        for scene_file in SCENES_DIR.iterdir():
            if scene_file.name == POST_PROCESSING_PARAMS_FILE.name:
                continue
            if scene_file.suffix == ".toml":
                print(f"Loading scene from file: {scene_file.name}")
                with open(scene_file, "rb") as f:
                    data = tomllib.load(f)

                data["params"] = [
                    self._generate_param_from_file_data(p)
                    for p in data.get("params", [])
                ]
                ascene = Scene(**data)
                self.scenes.append(ascene)
                print(f"Scene {ascene.name} loaded")

        # Reorder scenes according to scenes_order.json
        self._reorder_scenes()

    def _load_post_processing_params(self):
        with open(POST_PROCESSING_PARAMS_FILE, "rb") as f:
            data = tomllib.load(f)

        params_data = data.get("params", [])
        return [self._generate_param_from_file_data(p) for p in params_data]

    def _reorder_scenes(self):
        """Reorder scenes according to the order specified in scenes_order.json"""
        try:
            with open(SCENES_ORDER_FILE, "r") as f:
                config = json.load(f)

            scene_order = config.get("scene_order", [])
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
            print(f"Scenes reordered according to scenes_order.json")

        except FileNotFoundError:
            print(f"Warning: {SCENES_ORDER_FILE} not found. Using default order.")
        except (json.JSONDecodeError, KeyError) as e:
            print(
                f"Warning: Error parsing {SCENES_ORDER_FILE}: {e}. Using default order."
            )

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

        self.global_ctx.update_last_time(time)

        width, height = int(resolution[0]), int(resolution[1])

        # Apply resolution factor if specified
        if self.current_scene.res_factor is not None:
            fbo_width = int(width * self.current_scene.res_factor)
            fbo_height = int(height * self.current_scene.res_factor)
        else:
            fbo_width = width
            fbo_height = height

        # Resize FBO if needed
        if (
            self.fbo is None
            or self.fbo_texture.width != fbo_width
            or self.fbo_texture.height != fbo_height
        ):
            if self.fbo is not None:
                self.fbo.release()
            self.fbo_texture = self.screen_ctx.texture((fbo_width, fbo_height), 4)
            self.fbo_texture.filter = (self.screen_ctx.LINEAR, self.screen_ctx.LINEAR)
            self.fbo = self.screen_ctx.framebuffer([self.fbo_texture])

        # Create FBO resolution tuple for shader (aspect ratio based on FBO dimensions)
        fbo_resolution = (
            fbo_width,
            fbo_height,
            fbo_width / fbo_height if fbo_height > 0 else 1.0,
        )

        # Update parameters for both passes
        self._update_params(time, frame_time, fbo_resolution)
        self._update_post_params(time, frame_time, resolution)
        self.global_ctx.apply_speed_hold(frame_time)

        # FIRST PASS: Render scene to FBO
        self.fbo.use()
        self.fbo.clear()
        self.quad.render(self.current_prog)

        # SECOND PASS: Render FBO texture to screen with post-processing
        self.screen_ctx.screen.use()
        self.screen_ctx.clear()
        self.fbo_texture.use(0)
        # Re-bind textures in case they need to be refreshed
        self._bind_textures_to_shader()
        self.quad.render(self.post_prog)

    def _update_params(
        self, time: float, frame_time: float, resolution: Tuple[float, float, float]
    ):
        """
        Update shader uniforms with current parameter values for first pass

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self.current_prog is None:
            return

        if "iTime" in self.current_prog:
            adjusted_time = self.global_ctx.get_adjusted_time(time)
            self.current_prog["iTime"].value = adjusted_time

        if "iResolution" in self.current_prog:
            self.current_prog["iResolution"].value = resolution

        _ = frame_time  # for future use

        # Update shader parameters using the scene's method
        self.current_scene.update_shader_params(self.current_prog)

    def _update_post_params(
        self, time: float, frame_time: float, resolution: Tuple[float, float, float]
    ):
        """
        Update shader uniforms with current parameter values for second pass

        Args:
            time: Current time for animations
            frame_time: Time since last frame
            resolution: Screen resolution as (width, height, aspect_ratio)
        """
        if self.post_prog is None:
            return

        if "iResolution" in self.post_prog:
            self.post_prog["iResolution"].value = resolution

        if "iTime" in self.post_prog:
            self.post_prog["iTime"].value = time

        # Update post-processing shader parameters
        update_shader_params_from_list(self.post_prog, self.post_params)

    def change_to_next_scene(self, value: int | None = None):
        if value is not None and value != MIDI_BUTTEN_CLICK:
            return
        self._new_scene_index = (self.current_scene_index + 1) % len(self.scenes)

    def change_to_previous_scene(self, value: int | None = None):
        if value is not None and value != MIDI_BUTTEN_CLICK:
            return
        self._new_scene_index = (self.current_scene_index - 1) % len(self.scenes)

    def change_to_random_scene(self, value: int | None = None):
        if value is not None and value != MIDI_BUTTEN_CLICK:
            return
        available_scenes = [
            idx for idx, scene in enumerate(self.scenes) if scene != self.current_scene
        ]
        if available_scenes:
            self._new_scene_index = random.choice(available_scenes)

    def load_new_scene(self):
        self.current_scene_index = self._new_scene_index
        new_scene = self.current_scene
        print("=" * 80)
        print(f"Change to scene {new_scene.name}")
        self.global_ctx.reset_time_params()

        # Reset all post-processing parameters to initial values
        for param in self.post_params:
            if param.is_reset_on_scene_change:
                param.controller.reset()

        # Release old program if it exists
        if self.current_prog is not None:
            self.current_prog.release()

        # Load shader source code from the scene
        vertex_source, fragment_source = new_scene.get_shaders()

        # Create shader program
        self.current_prog = self.screen_ctx.program(
            vertex_shader=vertex_source, fragment_shader=fragment_source
        )
        self.quad = mglw.geometry.quad_fs()

        # Bind parameters and track them for future cleanup
        self.input_manager.unbind_params()
        for param in new_scene.params:
            if param.is_reset_on_scene_change:
                param.controller.reset()
            self.input_manager.bind_param(param)
            print(
                f"{param.name:20} {param.button.name:16}",
                " ".join(self.global_ctx.fake_midi.key_dict[param.button.name])
                if self.global_ctx.fake_midi
                else "",
            )
        print("=" * 80)
