from abc import ABC, abstractmethod

from params.params import Param


class InputManager(ABC):
    @abstractmethod
    def bind_param(self, param: Param):
        pass

    @abstractmethod
    def handle_input(self, **kwargs):
        pass


class KeyboardManager(InputManager):
    def __init__(self):
        self.bindings = {}

    def bind_param(self, param: Param):
        keys = param.button.value.keyboard_keys
        callbacks = param.controller.expose_functions()
        self.bindings.update(dict(zip(keys, callbacks)))

    def handle_input(self, key: int):
        self.bindings.get(key, lambda: None)()
