import tomllib
import json
from typing import List, Tuple
import os
import random
from pprint import pprint

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
        self._load_scens_from_toml_files()
        assert len(self.scenes) > 0, "No scenes are loaded."
        self._build_scene_index_map()
        self.init_general_funcs_bindings()
        self.current_scene_index = 0
        self.change_to_scene(self.current_scene)
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

    def _build_scene_index_map(self):
        """Build a mapping of scene names to their indices from config file"""
        try:
            with open('config/scenes_order.json', 'r') as f:
                config = json.load(f)
                scene_order = config.get('scene_order', [])

            # Create map based on config order
            ScenesManager.SCENE_INDEX_MAP = {name: idx for idx, name in enumerate(scene_order)}

            # Verify all loaded scenes are in the config
            loaded_scene_names = {scene.name for scene in self.scenes}
            configured_scene_names = set(scene_order)

            if loaded_scene_names != configured_scene_names:
                missing = loaded_scene_names - configured_scene_names
                extra = configured_scene_names - loaded_scene_names
                if missing:
                    print(f"WARNING: The following scenes found in TOML files but NOT listed in config/scenes_order.json:")
                    for scene in sorted(missing):
                        print(f"    - {scene}")
                if extra:
                    print(f"WARNING: The following scenes listed in config/scenes_order.json but their TOML files were not found:")
                    for scene in sorted(extra):
                        print(f"    - {scene}")

            # Reorder self.scenes list to match config order
            scenes_by_name = {scene.name: scene for scene in self.scenes}
            self.scenes = [scenes_by_name[name] for name in scene_order if name in scenes_by_name]

        except FileNotFoundError:
            print("Warning: config/scenes_order.json not found. Using default order.")
            ScenesManager.SCENE_INDEX_MAP = {scene.name: idx for idx, scene in enumerate(self.scenes)}

    def render(self, time, frame_time, resolution):
        if self.start_time is None:
            self.start_time = time

        if time - self.start_time > 3:
            self.change_to_next_scene()
            self.start_time = time

        self.current_scene.render(time, frame_time, resolution)

    def change_to_next_scene(self):
        self.current_scene_index = (self.current_scene_index + 1) % len(self.scenes)
        self.change_to_scene(self.current_scene)

    def change_to_previous_scene(self):
        self.current_scene_index = (self.current_scene_index - 1) % len(self.scenes)
        self.change_to_scene(self.current_scene)

    def change_to_random_scene(self):
        self.change_to_scene(random.choice(self.scenes))

    def change_to_scene_by_name(self, name: str):
        for scene in self.scenes:
            if name == scene.name:
                self.change_to_scene(scene)
                break

        else:
            raise ValueError(f'no scene named:\'{name}\' in {[s.name for s in self.scenes]}')

    def change_to_scene(self, new_csene: Scene):
        print(f'Change to scene {new_csene.name}')
        new_csene.setup(self.screen_ctx)
        for param in new_csene.params:
            self.input_manager.bind_param(param)


if __name__ == '__main__':
    sm = ScensManager()
