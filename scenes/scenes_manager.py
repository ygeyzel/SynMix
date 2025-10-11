import tomllib
from typing import List, Tuple
import os
from pprint import pprint

from inputs.input_manager import MidiInputManager
from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import controllers_registry
from scenes.scene import Scene


class ScenesManager:
    def __init__(self, screen_ctx):
        self.scenes = []
        self.input_manager = MidiInputManager() 
        self.screen_ctx = screen_ctx
        self._load_scens_from_toml_files()
        assert len(self.scenes) > 0, "Error! No scenes are loaded."
        self.current_scene = self.scenes[0]
        self.change_to_scene(self.current_scene)

        pprint(self.scenes)

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
    
    def render(self, time, frame_time, resolution):
        self.current_scene.render(time, frame_time, resolution)


    def change_to_scene(self, new_csene: Scene):
        new_csene.setup(self.screen_ctx)
        for param in new_csene.params:
            self.input_manager.bind_param(param) 

if __name__ == '__main__':
    sm = ScensManager()
