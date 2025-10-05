import tomllib
from typing import List, Tuple
import os
from pprint import pprint

from inputs.buttons import Button
from params.params import Param
from params.valuecontrollers import controllers_registry  
from scenes.scene import Scene


class ScensManager:
    def __init__(self):
        self.scenes = []
        self._load_scens_from_toml_files()
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



if __name__ == '__main__':
    sm = ScensManager()
