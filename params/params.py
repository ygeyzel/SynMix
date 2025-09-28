from params.valuecontrollers import ValueController
from inputs.buttons import Button


class Param:
    def __init__(self, name: str, button: Button, controller: ValueController):
        self.name = name
        self.button = button
        self.controller = controller

    def __repr__(self):
        return f'Param({self.name}, {self.button}, {self.controller})'

    @property
    def value(self) -> float:
        return self.controller.value

    def control_param(self, value: int | float):
        self.controller.control_value(value)
