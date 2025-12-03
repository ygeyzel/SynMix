from synmix.inputs.buttons import Button
from synmix.params.valuecontrollers import ValueController


class Param:
    def __init__(self, name: str, button: Button, controller: ValueController) -> None:
        self.name = name
        self.button = button
        self.controller = controller

    def __repr__(self) -> str:
        return f"Param({self.name}, {self.button}, {self.controller})"

    @property
    def value(self) -> float:
        return self.controller.value

    @property
    def is_reset_on_scene_change(self) -> bool:
        return not self.controller.is_persistent

    def control_param(self, value: float) -> None:
        self.controller.control_value(value)
