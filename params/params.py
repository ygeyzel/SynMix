from params.valuecontrollers import ValueController
from inputs.buttons import Button


class Param:
    def __init__(self, name: str, button: Button, controller: ValueController):
        self.name = name
        self.button = button
        self.controller = controller

    @property
    def value(self):
        return self.controller.value
